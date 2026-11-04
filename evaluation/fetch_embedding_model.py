"""Download only the public model files pinned in embedding_model.json.

    python -m evaluation.fetch_embedding_model --output .models/bge-small-en-v1.5
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


def verify_model(root, spec):
    root=Path(root).resolve()
    for item in spec['files']:
        path=(root/item['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Model file path escapes model directory')
        if not path.is_file():
            raise ValueError(f'Model file missing: {item["path"]}; run the explicit fetch command first')
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if path.stat().st_size!=item['bytes'] or digest!=item['sha256']:
            raise ValueError(f'Model file hash mismatch: {item["path"]}')


def fetch(root, spec):
    root=Path(root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    for item in spec['files']:
        path=(root/item['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Model file path escapes model directory')
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']:
            continue
        url=item['url']
        expected=f'https://huggingface.co/{spec["export_repository"]}/resolve/{spec["revision"]}/'
        if not url.startswith(expected):
            raise ValueError('Download URL is not the pinned public model repository')
        with urlopen(Request(url,headers={'User-Agent':'StudyRAG-local-retrieval'}),timeout=120) as response:
            data=response.read()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError(f'Download hash mismatch: {item["path"]}')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        print('Verified',item['path'],flush=True)
    verify_model(root,spec)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    spec=json.loads(Path(__file__).with_name('embedding_model.json').read_text(encoding='utf-8'))
    fetch(args.output,spec)
