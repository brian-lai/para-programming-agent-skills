# Plan: {TASK}

**Objective:** {observable outcome}
**Context:** {research path/revision and relevant facts}

## Contract and scope

Existing contract: {path/symbol and relevant behavior}. Add a spec only when a new/changed boundary requires one. Describe source interfaces/stubs only when necessary; create them in the execution checkout.

{Material scope choices and rationale. Include architecture, dependencies, degradation and observability only when affected.}

## Implementation Steps

- [ ] {Behavior-sized change phrased as a commit message}
  - Change: {verified paths/symbols; intended behavior and edge cases; useful nearby pattern}
  - Validation: {command, working directory and expected outcome; observe failure then fix for testable behavior}
  - Dependencies/recovery: {needed prior results; consequential prerequisites with observed/assumed availability; mismatch requiring investigation. Omit when immaterial.}
  - Required checks pass before committing this item; record commit before marking complete.

## Risks

{Material risk, mitigation and recovery; omit speculative boilerplate.}

## Success Criteria

{Observable behavior/artifact and required validation. Unmeasured metrics remain unknown.}

## Step example (omit from generated plans)

For the calculator fixture: change `calculator.py:ratio(total, count)` to preserve `total / count` for nonzero count; validate `ratio(10, 2) == 5` and the existing zero-count contract with `python3 -m unittest discover -p "test_*.py"` from the execution root. Confirm the actual source contract before using this example; do not infer a new zero-count behavior.
