"""Build a public-source ZIP with hashes, excluding local state and model weights."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = {'.github', 'components', 'docs', 'evaluation', 'examples', 'scripts', 'src', 'tests'}
FILES = {'.env.example', '.gitattributes', '.gitignore', '.python-version', 'CONTRIBUTING.md', 'LICENSE', 'README.md', 'app.py', 'pytest.ini'}
EXCLUDED_PARTS = {'.git', '.venv', '.retrieval-venv', '.models', '__pycache__', '.pytest_cache', 'local-results', 'tmp', 'temp'}
SECRET_PATTERNS = [
    re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}'),
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}'),
    re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
]


def public_files(root):
    root = Path(root).resolve()
    selected = []
    for path in root.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if any(part == '.env' or part.startswith('.env.') for part in relative.parts) and relative.as_posix() != '.env.example':
            continue
        if path.suffix in {'.onnx', '.bin', '.pyc', '.pyo'} or path.name == 'secrets.toml':
            continue
        allowed = relative.parts[0] in DIRECTORIES or relative.as_posix() in FILES
        allowed = allowed or (len(relative.parts) == 1 and relative.name.startswith('requirements') and path.suffix == '.txt')
        if allowed:
            selected.append(relative)
    return sorted(selected, key=lambda p: p.as_posix())


def build(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('Archive already exists; choose a new output path')
    records = []
    for relative in public_files(root):
        data = (root/relative).read_bytes()
        if relative.suffix.lower() not in {'.pdf', '.png', '.npz'}:
            text = data.decode('utf-8', errors='replace')
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                raise ValueError(f'Possible embedded credential/private key in {relative.as_posix()}; value withheld')
        records.append({'path': relative.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    if not records:
        raise ValueError('No public source files found')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for record in records:
            archive.write(root/record['path'], arcname='studyrag/'+record['path'])
        manifest = {'package': 'StudyRAG public source', 'files': records,
                    'excludes': 'Git history, local environments, environment secrets, model weights and scratch output',
                    'note': 'File hashes preserve the frozen evaluation byte identities. Verify before redistribution.'}
        archive.writestr('studyrag/PACKAGE_MANIFEST.json', json.dumps(manifest, indent=2)+'\n')
    return {'output': str(output), 'files': len(records), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('dist/studyrag-source.zip'))
    args = parser.parse_args()
    try:
        print(json.dumps(build(ROOT, args.output), indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Packaging failed: {exc}\n')
