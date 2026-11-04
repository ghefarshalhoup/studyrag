"""Integrity checks, including corrupt-label and premature-review failure cases."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from validate_dataset import validate

SOURCE = Path(__file__).resolve().parent

class DatasetValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'pilot'
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns('__pycache__'))

    def questions(self):
        return [json.loads(line) for line in (self.root/'questions.jsonl').read_text(encoding='utf-8').splitlines()]

    def save(self, questions):
        (self.root/'questions.jsonl').write_text(''.join(json.dumps(q)+'\n' for q in questions),encoding='utf-8')

    def test_valid_pilot(self):
        result=validate(self.root)
        self.assertEqual((result['documents'],result['questions'],result['answerable']),(12,20,16))

    def test_source_edit_is_detected(self):
        path=self.root/'corpus'/'classes.rst'
        path.write_bytes(path.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'Source hash mismatch'):
            validate(self.root)

    def test_quote_corruption_is_detected(self):
        q=self.questions(); q[0]['evidence'][0]['quote']='invented evidence'; self.save(q)
        with self.assertRaisesRegex(ValueError,'evidence quote mismatch'):
            validate(self.root)

    def test_offsets_must_match_lines(self):
        q=self.questions(); q[0]['evidence'][0]['start_char']+=1; self.save(q)
        with self.assertRaisesRegex(ValueError,'offsets disagree'):
            validate(self.root)

    def test_duplicate_ids_are_rejected(self):
        q=self.questions(); q[1]['question_id']=q[0]['question_id']; self.save(q)
        with self.assertRaisesRegex(ValueError,'Duplicate question ID'):
            validate(self.root)

    def test_unanswerable_cannot_have_evidence(self):
        q=self.questions(); q[-1]['evidence']=q[0]['evidence']; self.save(q)
        with self.assertRaisesRegex(ValueError,'unanswerable question has evidence'):
            validate(self.root)

    def test_drafts_fail_review_gate(self):
        q=self.questions()
        for row in q:
            row['review_status']='draft'; row['reviewer']=None
        self.save(q)
        with self.assertRaisesRegex(ValueError,'label is not reviewed'):
            validate(self.root,require_reviewed=True)

    def test_accepted_requires_reviewer(self):
        q=self.questions(); q[0]['review_status']='accepted'; q[0]['reviewer']=None; self.save(q)
        with self.assertRaisesRegex(ValueError,'reviewed label needs a reviewer'):
            validate(self.root)

    def test_named_review_passes_gate(self):
        q=self.questions()
        for row in q:
            row['review_status']='accepted'; row['reviewer']='test fixture only'
        self.save(q)
        self.assertEqual(validate(self.root,require_reviewed=True)['review_status'],{'accepted':20})

    def test_ai_review_is_distinguished_from_human_acceptance(self):
        q=self.questions()
        for row in q:
            row['review_status']='ai_reviewed'; row['reviewer']='Codex (AI)'
        self.save(q)
        self.assertEqual(validate(self.root,require_reviewed=True)['review_status'],{'ai_reviewed':20})

    def test_ai_review_requires_a_reviewer(self):
        q=self.questions(); q[0]['review_status']='ai_reviewed'; q[0]['reviewer']=None; self.save(q)
        with self.assertRaisesRegex(ValueError,'needs a reviewer'):
            validate(self.root)

    def test_exposed_pilot_cannot_become_test(self):
        q=self.questions(); q[0]['split']='test'; self.save(q)
        with self.assertRaisesRegex(ValueError,'development-only'):
            validate(self.root)

if __name__=='__main__':
    unittest.main()
