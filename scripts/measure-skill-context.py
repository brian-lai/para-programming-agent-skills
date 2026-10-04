#!/usr/bin/env python3
"""Measure declared instruction paths in UTF-8 bytes, not model tokens."""
import argparse
import json
from pathlib import Path
import sys


def measure(root, manifest, baseline):
    root = Path(root).resolve()
    if manifest['scenarios'].keys() != baseline['scenarios'].keys():
        raise ValueError('missing or unexpected scenario')
    files, scenarios = {}, {}
    for name, scenario in manifest['scenarios'].items():
        paths = scenario['paths']
        if len(paths) != len(set(paths)) or not set(scenario['required_resources']) <= set(paths):
            raise ValueError(name + ': duplicated path or mandatory resource omitted')
        for path in paths:
            source = (root / path).resolve()
            if not source.is_relative_to(root):
                raise ValueError('path outside root')
            raw = source.read_bytes()
            entry = {'bytes': len(raw), 'words': len(raw.decode('utf-8').split())}
            if source.name == 'SKILL.md':
                parts = raw.split(b'---', 2)
                if len(parts) != 3:
                    raise ValueError('missing frontmatter: ' + path)
                entry.update(metadata_bytes=len(parts[1]) + 6, body_bytes=len(parts[2]))
            files[path] = entry
        size = sum(files[p]['bytes'] for p in paths)
        scenarios[name] = {'bytes': size, 'words': sum(files[p]['words'] for p in paths),
            'baseline_bytes': baseline['scenarios'][name]['bytes'], 'paths': paths,
            'within_budget': size <= baseline['scenarios'][name]['bytes']}
    return {'metric': 'UTF-8 bytes and whitespace words; declared unique-file paths, not runtime tokens',
            'files': files, 'scenarios': scenarios, 'within_budget': all(s['within_budget'] for s in scenarios.values())}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.')
    p.add_argument('--manifest', default='tests/fixtures/skill-context-budget.json')
    p.add_argument('--baseline', default='tests/fixtures/skill-context-baseline.json')
    p.add_argument('--out')
    args = p.parse_args()
    try:
        result = measure(args.root, json.loads(Path(args.manifest).read_text()), json.loads(Path(args.baseline).read_text()))
        if args.out:
            Path(args.out).write_text(json.dumps(result, indent=2) + '\n')
        for name, s in result['scenarios'].items():
            print(f'{"PASS" if s["within_budget"] else "FAIL"} {name}: {s["bytes"]} / {s["baseline_bytes"]} bytes')
        return 0 if result['within_budget'] else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr);return 2


if __name__ == '__main__':
    raise SystemExit(main())
