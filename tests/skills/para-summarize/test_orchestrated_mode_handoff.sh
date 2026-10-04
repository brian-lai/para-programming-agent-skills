#!/usr/bin/env bash
set -euo pipefail
grep -q 'Return to the orchestrator' skills/para-summarize/SKILL.md
grep -q 'does not mark' skills/para-summarize/SKILL.md
echo 'PASS summary returns without claiming merge'
