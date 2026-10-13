"""Trusted validation programs. Execute returned code only in the isolated validator."""
from handoff import HANDOFF_CASES


def contract_code(case):
    if case not in HANDOFF_CASES:
        raise ValueError('unknown handoff validator case')
    if case == 'handoff_dependency':
        return '''from pricing import subtotal
from invoice import total
assert subtotal([(10, 3), (2, 4)]) == 38
assert subtotal([]) == 0
assert total([(10, 3)]) == 35
assert total([(10, 5)]) == 50
assert total([(10, 6)]) == 60
assert total([(0, 3)]) == 0
assert total([]) == 0
'''
    start = 'from metrics import average as calculate\n' if case == 'handoff_stale' else 'from calculator import ratio as calculate\n'
    return start + '''for numerator, count in ((10, 2), (10, -2), (-9, 3), (0, 5), (7, 1)):
 assert calculate(numerator, count) == numerator / count
try:
 calculate(10, 0)
except ValueError:
 pass
else:
 raise AssertionError('zero count must raise ValueError')
'''


def validation_code(case):
    checks = contract_code(case)
    no_old_api = "assert not Path('/tmp/validate-code/calculator.py').exists()\n" if case == 'handoff_stale' else ''
    return '''import json, subprocess, sys
from pathlib import Path
subprocess.run(['git', 'clone', '--no-checkout', sys.argv[1], '/tmp/validate-code'], check=True, capture_output=True)
subprocess.run(['git', '-C', '/tmp/validate-code', 'checkout', sys.argv[2]], check=True, capture_output=True)
assert any(Path('/tmp/validate-code').glob('test_*.py')), 'meaningful regression tests required'
sys.path.insert(0, '/tmp/validate-code')
''' + no_old_api + checks + '''r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-p', 'test_*.py'], cwd='/tmp/validate-code', capture_output=True, text=True)
print(json.dumps({'returncode': r.returncode, 'output': r.stdout + r.stderr}))
sys.exit(r.returncode)
'''
