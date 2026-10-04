# Skill evaluation

These development tools evaluate instructions; installed skills do not depend on them. Structural tests check packaging and declared contracts. Fixture/grader tests exercise the evaluation machinery. Only recorded runs of an actual agent host count as behavioral trials.

## Inputs and evidence

`python3 scripts/evaluate-skills.py prepare --case CASE --out NEW_DIRECTORY [--variant 0|1|2]` creates a disposable real Git repository, local bare remote, primary context and a private service record. It refuses an existing destination. The acceptance matrix is `tests/fixtures/workflow-cases.json`; fixture code and matrix jointly determine case_version. Status variants cover research-only, branch-only, and per-phase summarized-but-unmerged states.

The local GitHub substitute supports repository identity, PR lookup/create/view/diff/checks and guarded merge. Unknown operations fail without contacting GitHub. Merge updates the bare repository's real base and can inject a concurrent head change. It does not validate real GitHub API compatibility, authentication or branch protections.

A host adapter runs in native filesystem/network isolation with only fixture inputs, selected skill revision, matching global methodology and a local bare remote. Grading runs outside agent-writable storage. The agent cannot write native transcripts, host manifests, judgments or service events. Never execute fixture code on the user's host as part of grading.

Capture these artifacts outside the agent's mount:

- `initial.json`: original fixture identity, version, revision, context and preservation sentinels.
- `host.json`: host/version, exact model, settings including frozen limits, skill_revision, trial, case_version, elapsed_seconds, termination_reason, evidence_kind (`native_agent` or explicitly synthetic tooling test), and tool_calls when observable.
- `transcript.jsonl`: unchanged native JSONL stream, including subagent events when supported and terminal usage. No fabricated completion transcript.
- `service/state.json` and append-only `service/events.jsonl`: independently collected effects. Git history/worktrees and context files supply final-state evidence.
- `judgment.json` for planning/review/status quality: transcript_sha256, rubric_version, pass, rationale, unsupported_findings and questions. Record the evaluator and any uncertainty; missing judgment leaves quality incomplete.

`python3 scripts/evaluate-skills.py grade --case CASE --run DIRECTORY --out RESULT.json` returns 0 for pass, 1 for failed assertions, 2 for missing/invalid evidence. Results include assertion evidence/criticality, observed outcomes, revisions/settings, artifact hashes, elapsed time, usage and termination reason. Missing telemetry is null. Claims such as “done” are not proof of completion. Malformed/out-of-fixture imported paths must not be followed.

## Calibrated judgment rubric (v1)

Calibrate before trials using obvious positive/negative examples, then keep the rubric fixed:

- Documentation plan: pass a typo-scoped plan with a concrete diff/manual check and preserved PR policy; fail invented runtime scaffolding, unnecessary design questions or mandatory unrelated test suites. An optional irrelevant section is a quality cost, not data loss.
- Review: the seeded denominator change is a defect (e.g. ratio(10,2) becomes 10/3); quote style is a preference. Pass when the defect has a correct trigger/impact and style does not block approval. Count unsupported blockers separately.
- Status: report the actual variant with a useful next action and no state mutation; never call summarized-unmerged work completed.

Human or agent judgments remain fallible. Report who judged, calibration examples and disagreements; deterministic evidence and subjective judgments are separate assertions. Small samples diagnose regressions, not general superiority.

## Measurement and paired comparisons

`python3 scripts/measure-skill-context.py --root REVISION_CHECKOUT --manifest tests/fixtures/skill-context-budget.json --baseline tests/fixtures/skill-context-baseline.json --out METRICS.json` counts each declared required file once, reports metadata/body sizes separately, and returns 1 for growth or 2 for invalid input. Optional resource load conditions are explicit. The reviewed manifest does not automatically discover every actual read; inspect native traces for extra/repeated reads and generated artifacts.

`python3 scripts/evaluate-skills.py compare --baseline BASELINE_RESULTS --candidate CANDIDATE_RESULTS --out COMPARISON.json` requires one result JSON per trial in each directory. Pair by case/version/variant/trial and require identical model, host version and settings. Keep failures/timeouts and identify incomplete harness runs. Mixed revisions are labeled and partitioned; do not present them as one final-candidate run. Universal simple-plan orchestration is reported separately as an added capability.

Before measurement, pilot one full simple lifecycle per arm. Freeze fixtures, model, settings, isolation and limits after pilots. Defaults: targeted cases 600 seconds/100 aggregate tool calls; simple lifecycle 1200/200; two-phase lifecycle 1800/300. The external capture function preserves partial transcripts on timeout or observed tool limit. Include child tool events when the host exposes them; otherwise disclose unobservable counts. A Docker adapter must also stop its named container after timeout; killing only the docker client does not stop a container.

Run three paired trials for each of the ten core cases and the two held-out cases, with seeded randomized arm order and fresh fixtures. Record pilots separately. Review held-out results before using them to tune guidance. Instruction fixes identify exact revisions and affected cases; shared workflow/schema changes require rerunning all lifecycle cases. Report final-revision coverage and every case not rerun.
