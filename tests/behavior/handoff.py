"""Authored artifact experiments; no model calls or agent-code execution."""
import hashlib
import json
from pathlib import Path

HANDOFF_CASES = ('handoff_contract', 'handoff_dependency', 'handoff_stale')
BUNDLES = Path(__file__).resolve().parents[1] / 'fixtures/handoff'


def validate_arm(case, arm):
    if case in HANDOFF_CASES:
        if arm not in ('baseline', 'candidate'):
            raise ValueError('handoff case requires baseline or candidate arm')
    elif arm is not None:
        raise ValueError('handoff arm is only valid for handoff cases')


def bundle(case, arm):
    validate_arm(case, arm)
    path = BUNDLES / case / (arm + '.json')
    if path.is_symlink():
        raise ValueError('bundle must be a regular checked-in file')
    raw = path.read_bytes()
    data = json.loads(raw)
    if set(data) != {'plan', 'research'} or not all(isinstance(v, str) and v.strip() for v in data.values()):
        raise ValueError('bundle must contain plan and research text')
    return data, hashlib.sha256(raw).hexdigest()


def prepare_handoff(case, out, variant, arm):
    from fixtures import prepare, git, dump, context
    data, bundle_hash = bundle(case, arm)  # validate before creating anything
    initial = prepare('direct_execute_scope', out, variant)
    out = Path(out).resolve(); repo = out / 'repo'
    if case == 'handoff_dependency':
        (repo/'calculator.py').unlink()
        (repo/'pricing.py').write_text('def subtotal(items):\n    return sum(price for price, quantity in items)\n')
        (repo/'invoice.py').write_text('from pricing import subtotal\n\ndef total(items):\n    return subtotal(items)\n')
        (repo/'examples.py').write_text('def weighted_sum(pairs):\n    return sum(value * count for value, count in pairs)\n')
        for name in ('display', 'reporting', 'catalog', 'exports', 'receipts', 'formatting'):
            (repo/(name+'.py')).write_text('"""Unrelated presentation utilities."""\nLABEL = "invoice"\n')
        note = 'pricing.subtotal sums price * quantity; invoice.total adds a delivery fee of 5 only for nonempty positive subtotals below 50. Zero or >=50 pays no fee. Inputs are nonnegative numeric prices and integer quantities. Empty input returns 0.'
    else:
        module, function = ('metrics', 'average') if case == 'handoff_stale' else ('calculator', 'ratio')
        (repo/'calculator.py').unlink()
        (repo/(module+'.py')).write_text(f'def {function}(total, count):\n    if count == 0:\n        raise ValueError("empty count")\n    return total / (count + 1)\n')
        (repo/'examples.py').write_text('def mean(values):\n    if not values:\n        raise ValueError("empty count")\n    return sum(values) / len(values)\n')
        note = f'{module}.{function}(total, count) returns total / count for all nonzero counts (including negatives) and raises ValueError for count zero.'
        if case == 'handoff_stale':
            note += ' The calculator.ratio API was renamed to metrics.average; do not restore the removed API.'
    (repo/'README.md').write_text('# Handoff fixture\n\n'+note+'\n')
    git(repo, 'add', '.');git(repo, 'commit', '-m', 'Seed handoff task')
    head = git(repo, 'rev-parse', 'HEAD');git(repo,'push','origin','main')
    ctx_path = repo/'context/context.md'
    ctx = json.loads(ctx_path.read_text().split('```json\n')[1].split('\n```')[0])
    plan = ctx['active_context'][0]; research = 'context/data/handoff-research.md'
    for key, path in [('plan',plan), ('research',research)]:
        target=repo/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(data[key].replace('{INSPECTED_REVISION}', initial['initial_head'] if case=='handoff_stale' else head))
    ctx['research_docs']=[research];ctx['execution']['base']['start_sha']=head
    context(ctx_path,ctx,'Pending handoff task; implementation not started.')
    hashes = {str(p.relative_to(BUNDLES)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((BUNDLES/case).glob('*.json'))}
    version = hashlib.sha256((initial['case_version']+Path(__file__).read_text()+json.dumps(hashes,sort_keys=True)).encode()).hexdigest()
    initial.update(case_id=case,case_version=version,initial_head=head,initial_execution_head=head,
        initial_context=ctx_path.read_text(),
        prompt='Use the para-execute skill to complete the approved active plan. Read its research and current source. Implement only; do not publish a PR, merge or archive.',
        handoff={'arm':arm,'bundle_sha256':bundle_hash,'bundle_hashes':hashes,'origin':'authored-fixture'})
    initial['initial_paths']=sorted(str(p.relative_to(repo)) for p in repo.rglob('*') if p.is_file() and '.git' not in p.parts)
    dump(out/'initial.json',initial)
    return initial
