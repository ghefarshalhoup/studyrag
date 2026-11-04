"""Check the prospective held-out question freeze without running retrieval."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(root):
    root = Path(root)
    directory = root/'heldout-v1'
    frozen = json.loads((directory/'freeze.json').read_text(encoding='utf-8'))
    for key, path in {
        'questions_sha256': directory/'questions.jsonl',
        'development_questions_sha256': root/'questions.jsonl',
        'corpus_manifest_sha256': root/'corpus_manifest.json',
        'chunks_sha256': root/'runs/bm25-v1/chunks.jsonl',
        'reranker_plan_sha256': root.parent/'reranker_plan.json',
    }.items():
        if sha(path) != frozen[key]:
            raise ValueError(f'Held-out freeze hash mismatch: {key}')
    manifest = json.loads((root/'corpus_manifest.json').read_text(encoding='utf-8'))
    sources = {}
    for doc in manifest['documents']:
        path = (root/doc['path']).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != doc['sha256']:
            raise ValueError('Corpus path/hash mismatch')
        sources[doc['document_id']] = path.read_text(encoding='utf-8')
    rows = [json.loads(line) for line in (directory/'questions.jsonl').read_text(encoding='utf-8').splitlines()]
    development = [json.loads(line) for line in (root/'questions.jsonl').read_text(encoding='utf-8').splitlines()]
    if len(rows) != frozen['question_count'] or len({q['question_id'] for q in rows}) != len(rows):
        raise ValueError('Held-out question count/identity mismatch')
    if {q['group_id'] for q in rows} & {q['group_id'] for q in development}:
        raise ValueError('Question family overlaps development data')
    if {q['question'].casefold().strip() for q in rows} & {q['question'].casefold().strip() for q in development}:
        raise ValueError('Question duplicates development data')
    for row in rows:
        if row['split'] != 'test' or row['review_status'] != 'ai_reviewed' or type(row['answerable']) is not bool:
            raise ValueError('Invalid held-out split/review/answerability')
        if not row['question'].strip() or not row['reference_answer'].strip() or not row['reviewer'].strip():
            raise ValueError('Missing question/review metadata')
        if row['answerable'] and not row['evidence']:
            raise ValueError('Answerable question lacks evidence')
        if not row['answerable'] and (row['evidence'] or not row.get('unanswerable_rationale')):
            raise ValueError('Invalid unanswerable evidence/rationale')
        for evidence in row['evidence']:
            text = sources[evidence['document_id']]
            lines = text.splitlines(keepends=True)
            a, b = evidence['start_line'], evidence['end_line']
            start, end = evidence['start_char'], evidence['end_char']
            if not 1 <= a <= b <= len(lines) or evidence['relevance'] != 2:
                raise ValueError('Invalid source line range/grade')
            if (start != sum(map(len, lines[:a-1])) or end != sum(map(len, lines[:b]))
                    or text[start:end] != evidence['quote'] or not evidence['quote'].strip()):
                raise ValueError('Evidence quote/offset mismatch')
        if not row['answerable']:
            terms = row.get('negative_search_terms', [])
            if not terms or any(not term.strip() for term in terms):
                raise ValueError('Missing negative search terms')
            if any(term.casefold() in text.casefold() for term in terms for text in sources.values()):
                raise ValueError('Negative search term appears in corpus; source review required')
    answerable = sum(q['answerable'] for q in rows)
    if answerable != frozen['answerable_count'] or len(rows)-answerable != frozen['unanswerable_count']:
        raise ValueError('Frozen answerability counts differ')
    return {'questions': len(rows), 'answerable': answerable, 'unanswerable': len(rows)-answerable,
            'family_overlap': 0, 'retrieval_calls': 0, 'review_status': 'ai_reviewed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=Path('evaluation/pilot'))
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.dataset), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Held-out validation failed: {exc}\n')
