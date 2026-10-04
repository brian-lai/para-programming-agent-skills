# Plan: {TASK}

**Objective:** {observable outcome}
**Context:** {research path/revision and relevant facts}

## Contract and scope

Existing contract: {path/symbol and relevant behavior}. Add a spec only when a new/changed boundary requires one. Describe source interfaces/stubs only when necessary; create them in the execution checkout.

{Material scope choices and rationale. Include architecture, dependencies, degradation and observability only when affected.}

## Implementation Steps

- [ ] {Behavior-sized change phrased as a commit message}
  - Files: {affected paths}
  - Validation: {specific failure/edge cases and check commands; observe failure then fix for testable behavior}
  - Required checks pass before committing this item; record commit before marking complete.

## Risks

{Material risk, mitigation and recovery; omit speculative boilerplate.}

## Success Criteria

{Observable behavior/artifact and required validation. Unmeasured metrics remain unknown.}
