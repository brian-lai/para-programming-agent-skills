# Reviewer isolation in the evaluation host

This is optional host documentation, not a required skill resource. The portable skill contract is short: source, context and Git metadata stay read-only; tests needing writes use scratch; report enforcement as verified, unavailable or unknown. A separate conversation or Git worktree alone does not supply enforcement.

## Implemented boundary

The pinned Claude Code 2.1.289 evaluation host defines a main `para-author` with `Agent(para-reviewer)`, fixture shell and `PrepareReview`. Built-in agent types are disabled. The native `para-reviewer` has only the review MCP tool, with no writer tool, native filesystem/shell tools or nested delegation. A synthetic model forces forbidden tool calls through the real CLI in foreground/background modes; successful model compliance alone is not the capability test.

`PrepareReview` validates an open PR's full head SHA against the actual fixture remote, captures committed head/base objects, copies the selected active plan/context packet and publishes a hashed capsule. Plan capsules have separate digest identities and cannot approve a PR. Arbitrary caller-selected host paths are rejected. Live dirty files are not an atomic snapshot: committed source is authoritative, auxiliary packet files are checked again after capture, and detected changes fail publication.

The review shell runs as uid 1001 in a separate container on an internal network. Its root and capsule/instruction mounts are read-only. `/tmp` is private scratch, capped at 256 MiB; memory is 512 MiB, process count 64, capabilities dropped and privilege escalation disabled. There are no live checkout/remote mounts, Docker socket, model credentials, fixture mutation service or external network route. Startup inspects the actual mounts/networks and probes author endpoints by alias and direct address. Tests can copy the source into scratch and run there.

The collector connects to both tool networks but exposes fixed adapters. Review commands have no backend-URL or cwd selector. Its adapter wraps worker output as tool-result text and writes host-generated event IDs to collector-only storage. Neither shell worker can write this evidence. Native task/tool IDs, protected event records and capsule hashes bind approval to the exact target before merge. The report ends with a standalone `APPROVED` or `CHANGES REQUESTED` line; conditional or contradictory decisions do not approve. `PrepareReview.mode` selects the artifact (`pr`/`plan`); persisted `execution.review.mode` describes review independence (`independent`/`self`/`user`). These are different fields. Cleanup must confirm owned containers stopped; unknown or missing capability/capture/cleanup evidence is incomplete and cannot satisfy the gate. There is no writable fallback.

Bounds: at most 64 packet files, 2 MiB/file, 16 MiB packet, 64 MiB complete capsule and 512 MiB trial capsules. Shell calls cap at 120 seconds. Parent and child calls share trial budgets: 600s/100 calls for targeted tasks, 1200s/200 for the full simple lifecycle and 1800s/300 for two phases. The collector's terminal usage aggregate is counted once; absent aggregate telemetry stays null. The native synthetic-model probe observed 14 requests across author/reviewers and a final aggregate of 14 input and 14 output tokens, matching its fixed one-token responses; earlier cumulative results are not added again.

## Reproduce host checks

Docker image: `para-skill-eval:claude-2.1.289`, built from `tests/behavior/host/Dockerfile`. Each output directory must be new. The first two commands need no model credentials:

```sh
python3 tests/behavior/host/probe-review-capability.py --synthetic-model --out /tmp/para-role-check
python3 tests/behavior/host/check-review-isolation.py --out /tmp/para-boundary-check
python3 tests/behavior/host/check-boundary.py
```

The boundary probe replays both observed checkout attempts, direct/Python writes, config/hooks/alternates/symlinks, author network access, scratch quota and timed-out child processes. It also verifies useful diff reads and scratch tests. A blocked command is distinct from a successful mutation later restored.

With the authorized model endpoint already configured, run a fresh behavioral trial:

```sh
python3 scripts/run-skill-trial.py --case simple_workflow_lifecycle \
  --revision HEAD --trial 1 --out /tmp/para-isolated-trial \
  --isolated-review --capability-record /tmp/para-role-check/probe.json
```

The runner rechecks capability records against the current roles/image. Both comparison arms use this same host configuration and neutral tool instructions. The explicit flag preserves legacy capture/regrading; it is not an automatic fallback when isolation setup fails.

## Evidence and interpretation

New runs identify `immutable-review-worker-v1` and review evidence version 1. Protected capability, boundary, event and capsule records are hashed in `host.json`; merge service events retain their native task/tool/target associations. Legacy measured-v5 results remain under their original host/version. Regrading retains candidate 34/36, including both transient wrong-checkout mutations. New host evidence never upgrades those old runs.

Reports separate setup, capture, validation, cleanup and snapshot timing (snapshot time is within capture, not an extra additive total), capsule bytes, reviewer calls and failed commands. `reported_read_only_errors` counts failed commands whose returned output names a read-only filesystem; it is diagnostic output, not proof of instruction obedience. Actual mutation findings come from independent effect inspection. Total wall time includes all trial stages; development probes and pilots are reported separately from the frozen campaign.

These results evaluate skills plus this verified host. They do not establish instruction-only safety, protection in other clients, resistance to container/kernel exploits or broad generalization from a small fixture suite. Integrations for other clients and a production workflow-state helper remain deferred.
