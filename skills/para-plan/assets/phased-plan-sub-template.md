# Phase {N}: {OUTCOME}

**Parent:** {master plan path}
**Prerequisite:** {predecessor merge and required base}
**Context:** {relevant contract/research paths and phase-critical facts}

## Scope and decisions

{Concrete outcome, boundaries and decisions needed for this phase; link shared detail instead of copying it.}

## Implementation Steps

- [ ] {Behavior-sized change phrased as a commit message}
  - Change: {verified paths/symbols; intended behavior and edge cases; useful nearby pattern}
  - Validation: {command, working directory and expected outcome; observe failure before fix for testable behavior}
  - Dependencies/recovery: {needed prior results; consequential prerequisites with observed/assumed availability; mismatch requiring investigation. Omit when immaterial.}
  - Required checks pass before commit; mark complete only after commit succeeds.

## Phase Gate and Recovery

{Acceptance criteria, required checks, meaningful risks/recovery. Review and merge before a dependent phase starts.}
