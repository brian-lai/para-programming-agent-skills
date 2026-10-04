#!/usr/bin/env python3
"""Development-time fixture preparation and evidence evaluation (not skill runtime)."""
import argparse
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests/behavior'))
from fixtures import prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--case', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--variant', type=int, default=0)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            value = prepare(args.case, args.out, args.variant)
            print(json.dumps({'case_id': value['case_id'], 'case_version': value['case_version'], 'root': str(Path(args.out).resolve())}))
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
