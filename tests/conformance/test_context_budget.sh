#!/usr/bin/env bash
# Static declared paths; live transcripts measure actual reads.
set -euo pipefail
python3 scripts/measure-skill-context.py \
  --root "${PARA_BUDGET_ROOT:-.}" \
  --manifest "${PARA_BUDGET_MANIFEST:-tests/fixtures/skill-context-budget.json}" \
  --baseline tests/fixtures/skill-context-baseline.json
