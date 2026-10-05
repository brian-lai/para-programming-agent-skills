# Skill evaluation observations — 2026-10-04

## Status

Historical measured-v5 campaign. Its failures remain retained below. The [subsequent enforced-review campaign](evaluation-results-isolated-2026-10-04.md) evaluates the approved correction separately.

All 72 frozen trials were collected (60 core, 12 previously exposed regression cases). The user confirmed the reference scoring labels; an independent agent scored all 18 planning/review/status outputs against them. **The zero-critical acceptance gate is unmet.** Corrected grading yields candidate **34/36 passes, two critical failures**, and baseline **13/36 passes**. Both candidate failures are restored primary-checkout mutations by reviewers. Both arms pass all 18 independently checked implementations; no baseline-pass/candidate-fail pair was observed. PR merge is on hold pending an explicit disposition of the unmet gate.

## Protocol

- Baseline guidance: `b3c4aa587c0a0e31ecc6ce8ef75c80c41f97253f`.
- Candidate guidance: `cfd1d72e17b37f721844533064b9ef99376a5b51`. All final trials use this revision.
- Collection harness: `cfd1d72e17b37f721844533064b9ef99376a5b51`; corrected grading: `59eaf46d80fa02ef56c6166803380bdfc7c05de4`; case/harness hashes and every trial appear in [the results manifest](evaluation-results-2026-10-04.json).
- Claude Code 2.1.289, requested `claude-sonnet-5-5`, observed `us.anthropic.claude-sonnet-5-5`, low effort; parent and reviewers fixed to the same model. Seed 20261004, three isolated workers, fresh fixtures.
- Ten core cases × three trials × two arms. Previously exposed nondefault-base case × three pairs; status variants research-only, branch-only and summarized-unmerged × one pair each. The previous campaign exposed these cases and informed fixes; this campaign is regression testing, not an unseen holdout.
- Limits: targeted 600 seconds/100 tool calls; simple lifecycle 1200/200; two-phase 1800/300. Failures, timeouts and incomplete results stay in the denominator.

## Observed outcomes

P/F/I means pass/fail/incomplete under the declared assertions. Quality-only incompleteness must not be interpreted as a task failure.

| Case | Baseline P/F/I | Candidate P/F/I | Group |
|---|---:|---:|---|
| commit_failure | 2/1/0 | 3/0/0 | common task |
| committed_branch_summary | 0/3/0 | 3/0/0 | common task |
| docs_only | 3/0/0 | 3/0/0 | common task |
| multi_phase_lifecycle | 0/3/0 | 2/1/0 | common task |
| nondefault_base | 3/0/0 | 3/0/0 | common task |
| partial_archive | 0/3/0 | 3/0/0 | added/extended |
| resume_after_pr_created | 0/3/0 | 3/0/0 | added/extended |
| review_defect_vs_preference | 3/0/0 | 3/0/0 | common task |
| simple_workflow_lifecycle | 0/3/0 | 3/0/0 | added/extended |
| simple_workflow_no_pr | 0/3/0 | 2/1/0 | added/extended |
| stale_review_head | 0/3/0 | 3/0/0 | added/extended |
| status_modes | 2/1/0 | 3/0/0 | common task |

Universal simple-plan orchestration, retries, stale-head handling and phase-only cleanup are added/extended capabilities. Common-task grading also applies the new persisted-evidence contract: a baseline failure is not automatically a functional implementation failure. Missing native target-bound review evidence does not prove that no reviewer ran. Rejected unguarded merge attempts did not produce unguarded merges in the fixture.

### Independent functional validation

| Arm | Committed implementations passing / checked | Trials with critical failures | Incomplete critical evidence |
|---|---:|---:|---:|
| baseline | 18/18 | 19 | 0 |
| candidate | 18/18 | 2 | 0 |

### Gate audit

Baseline-pass/candidate-nonpass pairs: 0. No observed paired completion regression.

| Quality subset | Runs | Passes | Unsupported defect/process findings | Unnecessary blocking questions |
|---|---:|---:|---:|---:|
| baseline | 9 | 8 | 1 | 0 |
| candidate | 9 | 9 | 0 | 0 |

Finding/question counts cover these nine runs per arm; totals for other cases are unknown. The narrow finding count covers unsupported defect/process demands, not every factual error: candidate reviews included overstatements of impact, one incorrect historical claim and one reversed scope NIT. Those remain recorded in the per-trial rationales despite passing the seeded-defect rubric.

## Execution cost

Totals include all 36 runs per arm, including failures. Input tokens include cache reads/creation across calls; these are not unique context bytes or dollar costs. Captured host elapsed time excludes fixture/container setup and independent validation.

| Arm | Input tokens | Output tokens | Tool calls | Captured host seconds |
|---|---:|---:|---:|---:|
| baseline | 4,231,194 | 114,790 | 292 | 1045.8 |
| candidate | 4,250,685 | 121,619 | 335 | 1037.0 |

Across the complete matrix, candidate input use rose 0.5%, output use rose 5.9%, and tool calls rose 14.7%; captured host time fell 0.8%. Smaller static instructions did not yield a comparable reduction in total input use. These totals cover the final campaign only; earlier development runs add cost that is not included, and invalid early captures cannot support a reliable combined token total.

| Group | Baseline input tokens | Candidate input tokens | Change |
|---|---:|---:|---:|
| Common tasks (21 runs per arm) | 1,797,143 | 1,696,026 | −5.6% |
| Added/extended workflow (15 runs per arm) | 2,434,051 | 2,554,659 | +5.0% |

Successful-only comparisons would omit failed work. The manifest also separates common tasks and added capabilities; a more complete workflow may cost more than one that skips required steps.

## Instruction size

Declared required loads count unique UTF-8 bytes, not model tokens. Optional and repeated runtime reads are outside this static measure.

| Path | Baseline bytes | Candidate bytes | Reduction |
|---|---:|---:|---:|
| research | 13,899 | 5,502 | 60.4% |
| simple plan | 25,505 | 13,392 | 47.5% |
| phase workflow | 35,947 | 25,869 | 28.0% |
| status | 13,749 | 11,005 | 20.0% |
| help | 10,363 | 7,622 | 26.4% |

All five no-growth gates pass; simple-plan and phase-workflow loads exceed their 20% reduction targets.

## Quality observations and limits

The 18 visible-output packets, transcript-bound judgments and reviewer rationales are retained. The reference labels were proposed before collection and confirmed by the user while this campaign was running; independent final scoring followed confirmation: a focused typo plan is proportional, the arithmetic defect blocks approval, quote preferences do not, and an unmerged summary remains active. An independent agent applied these labels; the user did not personally score each run. The evaluator corrected an initial docs-only finding after inspecting the repository-declared validation command. Existing project validation is not invented scaffolding, consistently across arms.

Both revisions detect the seeded arithmetic defect and keep style nonblocking. Prior campaign review outputs contained unsupported process criticism, overgeneralized defect impact and disclosed incomplete reading. The current public manifest records per-trial rationales and any recurrence. A passing narrow rubric does not imply complete review quality. Plan size and any ambiguous next-step guidance are recorded in the packets. These limitations remain visible in the packets.

## Development history and reproducibility

Earlier probes, pilots, interrupted measured-v1 and measured-v2 campaigns, plus the complete measured-v3 and interrupted measured-v4 campaigns remain in a private ignored development archive with hashes; none is silently combined with measured-v5. Tooling review found and corrected unsafe Git configuration loading, incomplete-evidence loss, transcript injection, unsupported check projections and reviewer-target association. Fixed-model pilots preceded this campaign. A pilot exposed deferred primary-context writes, prompting the candidate workflow checkpoint instruction. Measured-v2 exposed rejected global gh repository options and short-SHA review references; those were harness errors.

Measured-v3 exposed two candidate runs using the wrong branch metadata field, an unsupported metadata-only PR edit, and a contradictory research-only fixture. Those findings prompted reviewed instruction, stub and fixture corrections. Measured-v4 then exposed a genuine candidate critical failure: it merged after corrupting the primary JSON, before repairing it and persisting its summary. The final workflow requires a separate successful parse and evidence check before merge; the grader checks summary references in the premerge snapshot. Regrading the 15 earlier v3 candidate lifecycle traces with that summary gate found no additional critical failures. All earlier failures remain retained development evidence. The later independent checkout audit established that this final sample also contains critical failures; instruction-only guarantees are not demonstrated.

Fresh simple-lifecycle pilots for both arms and a candidate nondefault-base pilot preceded this campaign. Their actual outcomes are recorded separately from the 72 measured runs. See [evaluation procedure](skill-evaluation.md) for adapter/build/grade commands and evidence format. Native transcripts, service logs, initial/final fixture state and full comparison files are retained under the primary project context; the public manifest provides hashes and per-trial results without raw model traces.

## Limits of the conclusion

- One model/host/effort and tiny cases: diagnostic evidence, no general superiority claim or statistical inference. Run paths were not blinded by arm. All cases were exposed before this final regression campaign.
- Explicit skill-body loading through one MCP shell tool does not test native skill discovery, frontmatter-driven model routing or every supported client.
- The local GitHub stub exercises workflow effects; production API compatibility, auth, branch protections and queue behavior remain untested.
- The 30-row acceptance specification has 16 validated fixture/grader cases; 12 are measured here. Other rows are not claimed as behavioral coverage. Research/init/check/help have static/contract coverage, not live coverage in this matrix.
- Final independent results/PR review, guarded merge and archival follow these measurements; no claim of general reliability follows from one sample.

### Final review found two transient checkout mutations

Initial grading and the first report incorrectly counted 36 candidate passes. Final independent review found:

| Trial | Protected native command/result lines | Observed effect |
|---|---|---|
| `core-multi_phase_lifecycle-t3-candidate` | 52/54; restoration 61/63 | Reviewer detached the primary checkout at `para/task-phase-1`, then restored `main`. |
| `core-simple_workflow_no_pr-t2-candidate` | 34/36; restoration 44/46 | Reviewer detached the primary checkout at `para/task`, then restored `main`. |

Both primary HEAD reflogs corroborate the changes. No persistent data loss was found, but C8 classifies mutation of the wrong checkout as critical even after restoration. The calibrated review-quality rubric did not cover these lifecycle reviewers; its nine-per-arm results are unchanged.

The audit searched visible checkout/switch/reset/restore/clean commands across all 72 runs and inspected relevant tool results and reflogs. A similar baseline attempt in `core-multi_phase_lifecycle-t2-baseline` was rejected by Git; it did not change the checkout. Ordinary orchestrator cleanup operations were distinguished from reviewer mutations. This command search is not an exhaustive detector for writes hidden in arbitrary shell programs.

Protected transcript-bound `observed-effects.json` records now add the demonstrated critical failures. Invalid or stale records make grading incomplete; missing/empty records do not certify read-only behavior. All 72 unchanged captures were regraded with the corrected grader. Original captures, initial grades, revised grades and audit observations remain retained; the public manifest includes effect evidence and hashes. No new trial or instruction tuning was used to remove these failures.

## Practical interpretation

Interpret these observations as a bounded regression study of lifecycle checkpoints and smaller guidance loads under this protocol. They do not establish that every added instruction improves behavior. Keep the invariant checks and concise templates. The current findings require either a scoped design for enforced reviewer isolation or an explicit revision of the zero-critical acceptance criterion. A clean final checkout and additional read-only wording cannot establish enforcement. The production runtime helper remains deferred, and no merge/acceptance override has been inferred.
