#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import yaml


def assemble(root: Path) -> tuple[dict, dict]:
    manifest_path = root / 'module_manifest.yaml'
    manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8')) or {}
    output: dict = {}

    for entry in manifest.get('modules', []):
        module_path = root / entry['path']
        module = yaml.safe_load(module_path.read_text(encoding='utf-8')) or {}
        if not isinstance(module, dict):
            raise ValueError(f'module must be a mapping: {module_path}')

        declared = set(entry.get('owns_top_level_keys', []))
        unexpected = set(module) - declared
        if unexpected:
            raise ValueError(f'undeclared top-level keys in {module_path}: {sorted(unexpected)}')

        duplicate = set(output) & set(module)
        if duplicate:
            raise ValueError(f'duplicate top-level keys: {sorted(duplicate)}')
        output.update(module)

    return manifest, output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', default=str(Path(__file__).parent))
    parser.add_argument('--out')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()

    root = Path(args.source_dir)
    manifest, output = assemble(root)
    target = Path(args.out) if args.out else root / manifest['assembly_target']
    rendered = yaml.safe_dump(output, allow_unicode=True, sort_keys=False, width=120)

    if args.check:
        current = yaml.safe_load(target.read_text(encoding='utf-8'))
        if current != output:
            print('assembled source differs from target')
            return 1
        print('assembled source matches target')
        return 0

    target.write_text(rendered, encoding='utf-8')
    print(target)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
