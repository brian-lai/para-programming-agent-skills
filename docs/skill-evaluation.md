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

## Verified host adapter

The local adapter uses Claude Code 2.1.289 with the configured `claude-sonnet-5-5` model, low effort, empty setting sources, no external MCP servers, and safe mode. A capability probe verified independent delegation. Bare mode exposed only Bash/Edit/Read and was rejected for lifecycle trials. We explicitly read the selected revision's skills/resources and inject its matching global methodology; this evaluates body guidance, not native skill discovery or metadata-driven model switching. Built-in host instructions remain consistent across arms.

Build the optional live-trial image (not needed by CI):

```bash
docker build -t para-skill-eval:claude-2.1.289 tests/behavior/host
python3 scripts/run-skill-trial.py --case simple_workflow_lifecycle --revision BASELINE_OR_CANDIDATE_SHA --trial 0 --out NEW_TEMP_DIRECTORY
```

The adapter accepts the already configured HTTPS model endpoint/auth environment without printing credentials. It creates an internal Docker network, mounts only the disposable repository/local remote plus read-only skill instructions and gh shim into the agent, and restricts outbound CONNECT traffic to the model endpoint. A separate gateway owns service state/events; the agent cannot mount them. Direct outbound access is probed before launching the host. Only generated container/network names are cleaned up. Transcripts and manifests stay on the host outside agent mounts; trial directories remain for inspection. Remove only a positively identified disposable trial directory after exporting evidence.

Pin the resulting image ID and archive it with the report: the Dockerfile pins CLI/Node versions, while OS package resolution can change on rebuild. Native streaming output and observed model names must be retained. Run `--probe` only for a delegation capability check; it is labeled separately and is not a task trial.

CI runs Python standard-library fixture/grader/measurement/comparison tests through `scripts/validate-skills.sh`, alongside existing conformance and installation checks. Layout compatibility remains a separate CI step. CI requires no model credentials, Docker daemon or network access for these deterministic tests; live trials are an explicit evaluation job.

For lifecycle cases, the adapter also clones the resulting bare base into a fresh validation container with no network or credentials, calls the required greeting/farewell functions, and runs unittest discovery. It saves `validation.json` outside agent mounts. This independently checks implemented behavior without executing agent-written code on the user's host. Missing collection is incomplete harness evidence; failed function/tests are task failures.

### Evidence boundary and current coverage

Git inspection runs against private snapshots containing regular objects, refs,
HEAD and index data only. Agent-owned config, hooks, external diff/merge drivers,
fsmonitor commands and object alternates are never loaded by the collector.
The gateway mounts only the fixture checkout (read-only), remote, service state,
and native transcript (read-only); it has no write access to host manifests,
validation results or transcripts. The agent container is removed before
independent validation starts, including on timeout or capture errors.

Each merge event saves the context **before** mutation and the native transcript
byte boundary. Eligibility requires checks actually returned for that PR/head,
a matching recorded approval already present, and a completed independent
reviewer for that head in the preceding native events. This adapter supports
Claude's forwarded child messages and completed task notifications, or a
synchronous tool result. Other exports require an adapter; a generic delegation
or a later approval cannot establish eligibility.

The 30-row acceptance matrix is a specification. Live fixture/grader coverage is
explicitly listed in `tests/behavior/graders.py:SUPPORTED` (the 12 measured cases
and four additional regression cases). Other rows currently return incomplete
and the live runner rejects them; generic seed creation is not validated coverage.
Existing conformance checks cover additional instruction contracts, but do not
establish agent behavior on those scenarios. Reports must retain this distinction.

Direct execution is validated at the committed execution head in a fresh,
network-free container; an empty commit or merely recording the base is
insufficient. Known critical failures remain recorded even when another part of
the evidence is incomplete. Missing critical counts are unknown in comparison
reports, and incomplete critical evidence is reported separately.

Interrupted `measured-v1` runs were development runs: independent review found
collector isolation and grading flaws before the campaign completed. Retain those
artifacts with the reason for exclusion; do not combine them with a new frozen
campaign. Simple-plan retry/stale-head fixtures and explicit partial archive are
extended workflow capabilities and reported separately from common tasks.

### Collector revision 3: shell isolation

The native CLI runs in a collector container without fixture mounts or native
shell/file tools. Its tools are restricted to native Agent delegation and one
MCP Bash tool. That adapter sends shell commands over the internal network to a
separate worker container containing the fixture. The worker has no model
credentials. Its response is always serialized as text inside an MCP tool result;
it cannot supply a native transcript envelope. File operations use this same
shell tool in both comparison arms. This changes the host tool interface, so
comparison trials must be restarted with identical adapter settings in both arms.

The fixed CLI's `--safe-mode` disables explicitly configured MCP servers too.
This adapter instead uses a fresh container home, empty setting sources, disabled
native skills, strict MCP configuration and an explicit native tool allowlist.
The actual tool scopes and built-in plugins are recorded in `host.json`; unexpected
tool scopes invalidate a run. The pinned host's built-in plugins are common to
both arms. No user-installed configuration, skills or plugins are mounted.

Run `python3 tests/behavior/host/check-boundary.py` explicitly for the credentials-free
Docker boundary probe. It reproduces a tool writing a fake event to worker PID 1
stdout, confirms that it appears only in worker logs, and verifies it cannot
become a collector event. Offline tests also verify arbitrary worker bytes remain
inside a text result. Legacy native runs without this boundary are incomplete.

Jq evidence supports an explicit deterministic subset: full check objects/arrays,
conclusion/state/bucket field projections and maps, and all-success predicates
listed in `supported_check_projection`. Whitespace outside string literals is
ignored. Time-dependent, constant and other unrecognized expressions cannot
establish passing checks; unsupported projections produce incomplete evidence.
No comparison between two arbitrary jq executions is used to infer dependency. Explicitly
projecting away checks remains an observed lack of a check read. Malformed native
JSONL is parsed line by line and does not discard independently recorded service
failures. Missing or invalid host evidence likewise cannot erase a logged unsafe
merge attempt. Both collector and worker absence must be confirmed through the
Docker daemon before independent validation starts.
