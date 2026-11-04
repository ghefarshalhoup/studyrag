"""Source-traceable chunks and a small, dependency-free BM25 baseline.

Only corpus text enters this module: questions and relevance labels do not affect
chunk preparation or index statistics. No LLMs, embeddings, or network calls.
"""
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import re

PREPROCESSOR_VERSION = 'rst-light-v1'
TOKENIZER_VERSION = 'unicode-word-casefold-v1'


@dataclass(frozen=True)
class ChunkConfig:
    size: int = 1200
    overlap: int = 200

    def validate(self):
        if type(self.size) is not int or type(self.overlap) is not int:
            raise ValueError('Chunk size and overlap must be integers')
        if self.size < 1 or not 0 <= self.overlap < self.size:
            raise ValueError('Require size > 0 and 0 <= overlap < size')


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source_sha256: str
    source_path: str
    start_char: int
    end_char: int
    start_line: int
    end_line: int
    text: str

    def record(self):
        return asdict(self)


def normalize_rst(text):
    """Light cleanup, not a full Sphinx renderer; raw coordinates stay separate.

    Remove standalone markup lines and role wrappers, preserving prose, headings,
    code, identifiers and numbers. Some indented directive content remains. Never
    execute directives or follow includes/links in a document.
    """
    lines = [line for line in text.splitlines()
             if not line.lstrip().startswith('.. ')
             and not re.fullmatch(r'\s*[-=~^#*+]{3,}\s*', line)]
    text = '\n'.join(lines)
    def role(match):
        value = match.group(1).lstrip('~!')
        return value.split(' <', 1)[0]
    text = re.sub(r':[\w:-]+:`([^`]+)`', role, text)
    text = re.sub(r'`([^`<>]+)\s+<[^>]+>`_?', r'\1', text)
    text = text.replace('`', '')
    return text.strip()


def tokenize(text):
    """Keep identifiers such as __main__; no stemming or query expansion."""
    return re.findall(r'\w+', text.casefold(), flags=re.UNICODE)


def make_chunks(document, raw_bytes, config=ChunkConfig()):
    config.validate()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest != document['sha256']:
        raise ValueError(f'Source hash mismatch: {document["document_id"]}')
    text = raw_bytes.decode('utf-8').replace('\r\n', '\n')
    line_starts = [0] + [m.end() for m in re.finditer('\n', text)]
    start = 0
    chunks = []
    while start < len(text):
        end = min(start + config.size, len(text))
        if end < len(text):
            boundary = text.rfind('\n', start + config.size // 2, end)
            if boundary >= start:
                end = boundary + 1
        content = normalize_rst(text[start:end])
        if tokenize(content):
            identity = {'document_id': document['document_id'], 'source_sha256':digest,
                        'config':asdict(config), 'preprocessor':PREPROCESSOR_VERSION,
                        'start_char':start, 'end_char':end}
            chunk_id = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
            chunks.append(Chunk(chunk_id,document['document_id'],digest,document['path'],
                                start,end,bisect_right(line_starts,start),
                                bisect_right(line_starts,end-1),content))
        if end == len(text):
            break
        next_start = max(start+1,end-config.overlap)
        # Prefer a complete next line; actual overlap never exceeds the budget.
        boundary = text.find('\n',next_start,end)
        start = boundary+1 if boundary >= 0 else next_start
    return chunks


class BM25:
    """Okapi BM25 with positive log1p IDF, k1=1.2, b=0.75.

    score=sum(idf(t)*tf(t)*(k1+1)/(tf(t)+k1*(1-b+b*dl/avgdl))).
    Query terms are deduplicated. Zero-score candidates are omitted, and ties are
    broken by stable chunk ID. Scores are rankings, not confidence probabilities.
    """
    def __init__(self, chunks, k1=1.2, b=.75):
        if not math.isfinite(k1) or k1 < 0 or not math.isfinite(b) or not 0 <= b <= 1:
            raise ValueError('Invalid BM25 parameters')
        self.chunks=list(chunks)
        if len({c.chunk_id for c in self.chunks}) != len(self.chunks):
            raise ValueError('Duplicate chunk IDs')
        self.k1,self.b=k1,b
        counts=[Counter(tokenize(c.text)) for c in self.chunks]
        self.lengths=[sum(c.values()) for c in counts]
        self.average_length=sum(self.lengths)/len(counts) if counts else 0
        self.postings=defaultdict(list)
        for i,terms in enumerate(counts):
            for term,frequency in terms.items():
                self.postings[term].append((i,frequency))

    def search(self, query, k=10):
        if type(k) is not int or k < 1:
            raise ValueError('k must be a positive integer')
        if not self.average_length:
            return []
        scores=defaultdict(float)
        n=len(self.chunks)
        for term in sorted(set(tokenize(query))):
            postings=self.postings.get(term,[])
            df=len(postings)
            if not df:
                continue
            idf=math.log1p((n-df+.5)/(df+.5))
            for i,tf in postings:
                norm=self.k1*(1-self.b+self.b*self.lengths[i]/self.average_length)
                scores[i]+=idf*tf*(self.k1+1)/(tf+norm)
        ranked=sorted(scores,key=lambda i:(-scores[i],self.chunks[i].chunk_id))[:k]
        return [(self.chunks[i],scores[i]) for i in ranked]


def covered_fraction(evidence, chunks):
    """Union raw source intervals; overlapping chunks must not count twice.

    This measures coverage of one known passage, not chunk relevance or answer
    correctness. It does not declare unannotated results irrelevant.
    """
    start,end=evidence['start_char'],evidence['end_char']
    if end <= start:
        raise ValueError('Evidence must be a nonempty interval')
    intervals=sorted((max(start,c.start_char),min(end,c.end_char)) for c in chunks
                     if c.document_id==evidence['document_id']
                     and c.start_char < end and c.end_char > start)
    total=0
    cursor=start
    for left,right in intervals:
        left=max(left,cursor)
        if right > left:
            total+=right-left
        cursor=max(cursor,right)
    return total/(end-start)


def evidence_diagnostics(question, chunks):
    positive=[e for e in question['evidence'] if e['relevance'] > 0]
    if not positive:
        return None
    fractions=[covered_fraction(e,chunks) for e in positive]
    return {'any_known_passage_complete':any(f==1 for f in fractions),
            'complete_passages':sum(f==1 for f in fractions),
            'known_positive_passages':len(positive),
            'mean_passage_character_coverage':sum(fractions)/len(fractions),
            'per_passage_coverage':fractions}
