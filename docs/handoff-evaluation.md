# Handoff evaluation protocol

**Status: NOT RUN.** No live model trial or production-run diagnosis was performed for this change. A model/endpoint and an authorized spending or enforceable usage ceiling have not been selected. Offline tests establish fixture, grader and comparison behavior; they do not establish improved model accuracy or efficiency.

## Questions and boundaries

The first pilot asks whether a fresh cheaper executor benefits from more actionable research/plan artifacts. Both arms use the same candidate skill revision. Baseline bundles follow the prior template; candidate bundles retain the same requirements and add implementation locations, examples and recovery detail. Bundles are authored examples, not outputs of an evaluated planning model. Their filenames do not imply a baseline-skill versus candidate-skill comparison.

Cases:

| Case | Task / observation |
|---|---|
| `handoff_contract` | Correct an existing arithmetic contract while preserving zero-count behavior. |
| `handoff_dependency` | Correct weighted subtotals, then apply a dependent delivery-fee rule; ignore unrelated modules. |
| `handoff_stale` | Reconcile a renamed API from stale research and correct the current implementation without restoring the removed API. |

A correct diagnosis of an unresolved conflict is not completed implementation. Report it separately; it remains unsuccessful for the completed-task metric. These fixtures are exposed pilot cases, not unseen holdouts.

## Freeze before collection

1. Confirm the cheaper executor's exact model ID, endpoint, host version and credentials through the configured host. Provider/model settings remain outside portable skills. The current native runner supports its Claude host; a successful run there is not evidence about another host or Luna.
2. Record a reviewed candidate SHA, harness/image identity, case versions and hashes of both bundles. Use identical skill revision, model/effort, tools, isolation and budgets across each pair. Fresh sessions receive artifacts and repository access, never a planner conversation.
3. Authorize the campaign ceiling before launching. Three cases × two arms × two repeats produces 12 executions. The runner's per-case bounds are 600 captured seconds and 100 observed aggregate calls, with children sharing the bound. Collection detects limits after observing events; one event can exceed a call bound. Setup/validation add time outside capture. These limits are not a dollar cap or a token ceiling; use an enforceable provider spending control when a hard monetary cap is required.
4. Predeclare a seeded randomized order of the 12 case/arm/repeat tuples. Keep failed/incomplete runs and all captures. Do not silently rerun or expand the campaign. A focused correction/rerun, at most once, needs room in the same authorized ceiling and a new declared revision.

Offline preparation (creates a new disposable fixture only):

```bash
python3 scripts/evaluate-skills.py prepare --case handoff_contract \
  --handoff-arm candidate --out /absolute/new/fixture
```

After configuration and campaign authorization, one native execution uses:

```bash
python3 scripts/run-skill-trial.py --case handoff_contract \
  --handoff-arm candidate --revision "$CANDIDATE_SHA" --model "$EXECUTOR_MODEL" \
  --trial 0 --out /absolute/new/candidate-contract-0
python3 scripts/evaluate-skills.py grade --case handoff_contract \
  --run /absolute/new/candidate-contract-0 --out /absolute/results/candidate/contract-0.json
```

Prepare parent result directories separately. The case output directory must not exist. See [skill evaluation](skill-evaluation.md) for host setup, limits and optional reviewer isolation; direct-execution cases do not invoke a reviewer. Keep raw outputs and secrets out of published reports.

After grading every attempted run, compare directories containing only corresponding grade JSON files:

```bash
python3 scripts/evaluate-skills.py compare \
  --baseline /absolute/results/baseline --candidate /absolute/results/candidate \
  --out /absolute/comparison.json
```

Pairing rejects missing/duplicate rows, changed executor settings, different skill revisions, mismatched bundle sets and swapped artifact arms. If a harness failure prevents a pair from being evaluated, retain and report that failure explicitly; do not silently delete it to obtain a valid comparison.

## Report and diagnose

Publish exact revisions/settings/hashes, task completion, failed and incomplete counts, critical findings, and raw tokens/calls/captured time. Cost per completed task includes all failed-attempt use in its numerator. Zero completions or missing required telemetry produces an unknown ratio. Parent aggregates already include children; do not count child tokens again. Dollars require recorded billing rates and usage categories; planner costs for authored bundles are unmeasured.

For visible-trace diagnosis, keep a small external annotation with `transcript_sha256`, evaluator, event IDs, category and reason. Categories: initial discovery, repeated discovery, implementation, validation/debugging, review, lifecycle bookkeeping, external waiting, unknown. Mark repeated reads/searches only when their earlier evidence remained applicable. Do not infer hidden reasoning. Parallel span durations may overlap; summed stage durations are not automatically total elapsed time. Record unsupported blockers, necessary/unnecessary questions and interventions with evidence.

A real slow-run trace can complement the fixture report when provided. None was supplied for this change. Manual classifications and small exposed fixtures support diagnosis, not universal performance claims. Any observed critical effect or candidate-only functional regression needs correction before promoting the implicated guidance.

## Follow-up gate: generated plans and full auto workflow

To support the user's actual end-to-end goal, a stronger model must generate research and an independently reviewed plan. A fresh cheaper executor then receives only those artifacts plus normal repository access and completes the authorized auto workflow through review, merge, archive and verified cleanup.

Compare matched tasks with fixed planner and executor settings within each baseline/candidate pair. Record research/planning cost, executor cost, review corrections, lifecycle bookkeeping, external waiting, failures and total wall time. Retain evidence through final archive; a merge without verified cleanup is incomplete. Reuse suitable existing lifecycle fixtures and add truly new tasks before claiming held-out validation. Evaluate another provider/host separately rather than pooling results into an unsupported portability claim.

This change documents that gate only. Automated planner integration, a second host and additional paid campaigns remain future work. Authored direct-execution results cannot satisfy the full-workflow gate.
