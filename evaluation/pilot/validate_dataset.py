"""Validate source integrity and pilot labels offline, using only the standard library."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

CATEGORIES = {'exact_term', 'paraphrase', 'typo', 'shorthand', 'multi_evidence', 'unanswerable'}
REQUIRED = {'question_id', 'split', 'group_id', 'category', 'question', 'answerable',
            'reference_answer', 'evidence', 'review_status', 'reviewer', 'review_notes'}
OPTIONAL = {'unanswerable_rationale', 'negative_search_terms'}
EVIDENCE_FIELDS = {'document_id', 'start_line', 'end_line', 'start_char', 'end_char',
                   'quote', 'relevance', 'rationale'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def local_path(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), f'Path outside dataset: {relative}')
    return path

def validate(root, require_reviewed=False):
    root = Path(root)
    manifest = json.loads((root / 'corpus_manifest.json').read_text(encoding='utf-8'))
    documents = manifest['documents']
    require(len(documents) == 12, 'Pilot requires 12 source documents')
    source_text = {}
    for doc in documents:
        doc_id = doc['document_id']
        require(doc_id not in source_text, f'Duplicate document ID: {doc_id}')
        data = local_path(root, doc['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == doc['sha256'], f'Source hash mismatch: {doc_id}')
        require(len(data) == doc['bytes'], f'Source size mismatch: {doc_id}')
        require(doc['source_commit'] == manifest['source_commit'], f'Commit mismatch: {doc_id}')
        source_text[doc_id] = data.decode('utf-8').replace('\r\n', '\n')
    license_bytes = local_path(root, manifest['license_path']).read_bytes()
    require(hashlib.sha256(license_bytes).hexdigest() == manifest['license_sha256'], 'License hash mismatch')
    questions = [json.loads(line) for line in (root / 'questions.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    require(len(questions) == 20, 'Pilot requires 20 questions')
    ids, groups, normalized = set(), {}, set()
    corpus = '\n'.join(source_text.values()).casefold()
    for q in questions:
        qid = q.get('question_id', '<missing ID>')
        require(REQUIRED <= q.keys() and q.keys() <= REQUIRED | OPTIONAL, f'{qid}: invalid question fields')
        require(qid.startswith('pilot-') and len(qid) == 9 and qid[6:].isdigit(), f'{qid}: invalid ID')
        require(qid not in ids, f'Duplicate question ID: {qid}')
        ids.add(qid)
        for field in ('question_id', 'group_id', 'question', 'reference_answer'):
            require(isinstance(q[field], str) and q[field].strip(), f'{qid}: invalid {field}')
        key = ' '.join(q['question'].casefold().split())
        require(key not in normalized, f'{qid}: duplicate question')
        normalized.add(key)
        require(q['split'] in {'dev', 'test'}, f'{qid}: invalid split')
        prior = groups.setdefault(q['group_id'], q['split'])
        require(prior == q['split'], f'{qid}: related question group crosses splits')
        # This exposed pilot is development-only; do not turn it into a claimed held-out test.
        require(q['split'] == 'dev', f'{qid}: pilot must remain development-only')
        require(q['category'] in CATEGORIES, f'{qid}: invalid category')
        require(type(q['answerable']) is bool, f'{qid}: answerable must be boolean')
        require(q['review_status'] in {'draft', 'ai_reviewed', 'accepted', 'revise', 'rejected'}, f'{qid}: invalid review status')
        require(q['reviewer'] is None or isinstance(q['reviewer'], str), f'{qid}: invalid reviewer')
        require(isinstance(q['review_notes'], str), f'{qid}: invalid review notes')
        if q['review_status'] in {'accepted', 'ai_reviewed'}:
            require(q['reviewer'] and q['reviewer'].strip(), f'{qid}: reviewed label needs a reviewer')
        if require_reviewed:
            require(q['review_status'] in {'accepted', 'ai_reviewed'}, f'{qid}: label is not reviewed')
        require(isinstance(q['evidence'], list), f'{qid}: evidence must be a list')
        if q['answerable']:
            require(q['category'] != 'unanswerable', f'{qid}: inconsistent category')
            require(any(e.get('relevance') in (1,2) for e in q['evidence']), f'{qid}: missing supporting evidence')
        else:
            require(q['category'] == 'unanswerable' and not q['evidence'], f'{qid}: unanswerable question has evidence')
            require(isinstance(q.get('unanswerable_rationale'), str) and q['unanswerable_rationale'].strip(), f'{qid}: missing absence rationale')
            terms = q.get('negative_search_terms', [])
            require(isinstance(terms,list) and terms, f'{qid}: missing absence search terms')
            require(all(isinstance(t,str) and t.strip() for t in terms), f'{qid}: invalid absence terms')
            require(not any(t.casefold() in corpus for t in terms), f'{qid}: absence search term found in corpus')
        spans = set()
        for e in q['evidence']:
            require(e.keys() == EVIDENCE_FIELDS, f'{qid}: invalid evidence fields')
            require(e['document_id'] in source_text, f'{qid}: unknown evidence document')
            require(type(e['relevance']) is int and e['relevance'] in (0,1,2), f'{qid}: invalid relevance')
            require(isinstance(e['rationale'],str) and e['rationale'].strip(), f'{qid}: missing relevance rationale')
            text = source_text[e['document_id']]
            lines = text.splitlines(keepends=True)
            first,last,start,end = (e[k] for k in ('start_line','end_line','start_char','end_char'))
            require(all(type(x) is int for x in (first,last,start,end)), f'{qid}: offsets must be integers')
            require(1 <= first <= last <= len(lines), f'{qid}: invalid line range')
            require(start == sum(map(len,lines[:first-1])) and end == sum(map(len,lines[:last])), f'{qid}: line/character offsets disagree')
            require(text[start:end] == e['quote'] and e['quote'].strip(), f'{qid}: evidence quote mismatch')
            key=(e['document_id'],start,end)
            require(key not in spans, f'{qid}: duplicate evidence span')
            spans.add(key)
        if q['category'] == 'multi_evidence':
            require(len({e['document_id'] for e in q['evidence'] if e['relevance'] > 0}) >= 2,
                    f'{qid}: multi-evidence pilot question needs two source documents')
    return {'documents':len(documents), 'questions':len(questions),
            'answerable':sum(q['answerable'] for q in questions),
            'categories':dict(Counter(q['category'] for q in questions)),
            'review_status':dict(Counter(q['review_status'] for q in questions))}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--require-reviewed',action='store_true',
                        help='Require AI-reviewed or human-accepted labels; does not imply human review')
    args=parser.parse_args()
    try:
        print(json.dumps(validate(args.root,args.require_reviewed),indent=2))
    except (ValueError,KeyError,TypeError,OSError) as exc:
        parser.exit(1,f'Validation failed: {exc}\n')
