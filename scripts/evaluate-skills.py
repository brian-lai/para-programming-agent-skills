#!/usr/bin/env python3
"""Development-time fixture preparation and evidence evaluation (not skill runtime)."""
import argparse
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests/behavior'))
from fixtures import prepare
from graders import grade


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--case', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--variant', type=int, default=0)
    g = commands.add_parser('grade')
    g.add_argument('--case', required=True)
    g.add_argument('--run', required=True)
    g.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            value = prepare(args.case, args.out, args.variant)
            print(json.dumps({'case_id': value['case_id'], 'case_version': value['case_version'], 'root': str(Path(args.out).resolve())}))
        elif args.command == 'grade':
            value = grade(args.run)
            if value.get('case_id', args.case) != args.case:
                raise ValueError('case/run mismatch')
            Path(args.out).write_text(json.dumps(value, indent=2) + '\n')
            return {'pass': 0, 'fail': 1, 'incomplete': 2}[value['outcome']]
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
