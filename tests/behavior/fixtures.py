"""Dispatch new experiments without changing legacy task/version inputs.

Legacy source and catalog retain their original bytes. Intentional changes to
those inputs change their version normally; adding a new family does not.
"""
from pathlib import Path
import legacy_fixtures
from legacy_fixtures import FIXED_ENV, git, dump, context
from handoff import HANDOFF_CASES, validate_arm, prepare_handoff

CASES = Path(__file__).resolve().parents[1] / 'fixtures/workflow-cases.json'
legacy_fixtures.CASES = CASES.with_name('legacy-workflow-cases.json')


def prepare(case_id, out, variant=0, handoff_arm=None):
    validate_arm(case_id, handoff_arm)
    if case_id in HANDOFF_CASES:
        return prepare_handoff(case_id, out, variant, handoff_arm)
    return legacy_fixtures.prepare(case_id, out, variant)
