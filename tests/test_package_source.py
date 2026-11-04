"""Public-source packaging boundaries and byte-preserving distribution."""
import hashlib
import json
import zipfile

import pytest

from scripts.package_source import build, public_files


def test_archive_preserves_bytes_and_excludes_local_private_files(tmp_path):
    root = tmp_path/'project'
    root.mkdir()
    examples = {
        'README.md': b'# Project\r\n', '.env.example': b'OPENAI_API_KEY=\n',
        '.gitattributes': b'* -text\n', 'evaluation/data.jsonl': b'{"source":"public"}\r\n',
        '.github/workflows/ci.yml': b'name: checks\n',
        '.env': b'PRIVATE=not-for-publication', '.env.local': b'PRIVATE=not-for-publication',
        '.git/config': b'private-repo-state', '.venv/installed.txt': b'local',
        '.models/model.onnx': b'weights', 'evaluation/model.onnx': b'weights',
        'local-results/results.json': b'{}', 'src/__pycache__/app.pyc': b'cache',
        'unrelated-private-notes.txt': b'private',
    }
    for name, data in examples.items():
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    expected = {'.env.example', '.gitattributes', 'README.md', 'evaluation/data.jsonl', '.github/workflows/ci.yml'}
    assert {p.as_posix() for p in public_files(root)} == expected
    output = tmp_path/'package.zip'
    result = build(root, output)
    assert result['files'] == len(expected)
    with zipfile.ZipFile(output) as archive:
        manifest = json.loads(archive.read('studyrag/PACKAGE_MANIFEST.json'))
        for record in manifest['files']:
            data = archive.read('studyrag/'+record['path'])
            assert data == examples[record['path']]
            assert hashlib.sha256(data).hexdigest() == record['sha256']
    with pytest.raises(ValueError, match='already exists'):
        build(root, output)


def test_embedded_credential_is_rejected_without_echoing_value(tmp_path):
    root = tmp_path/'project'
    root.mkdir()
    credential = 'sk-' + 'a'*30
    (root/'app.py').write_text('TOKEN = '+repr(credential))
    with pytest.raises(ValueError, match='value withheld') as exc:
        build(root, tmp_path/'unsafe.zip')
    assert credential not in str(exc.value)
    assert not (tmp_path/'unsafe.zip').exists()
