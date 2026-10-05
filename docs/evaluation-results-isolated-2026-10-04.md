# Enforced reviewer evaluation — 2026-10-04

## Acceptance decision

The new frozen campaign collected all **72/72** trials. Candidate guidance passes **36/36**, with **zero observed critical failures** and complete required evidence; baseline passes **11/36**. Both arms pass **18/18 independent implementation checks**, and no baseline-pass/candidate-nonpass pair was observed. The measured acceptance gates are satisfied for this host configuration. Final exact-head PR review, required checks, summary and guarded merge remain separate lifecycle gates.

The [original measured-v5 report](evaluation-results-2026-10-04.md) remains as historical evidence: candidate 34/36 with two restored reviewer checkout mutations. This correction adds an enforced review boundary to the evaluation host. It does not turn Markdown instructions into filesystem enforcement in other clients.

## Frozen protocol

- Candidate and collection/grading harness: `85fe5ee3d2d8f48f95751804c044a45ea40b61fa`. Baseline guidance: `b3c4aa587c0a0e31ecc6ce8ef75c80c41f97253f`.
- Claude Code 2.1.289, requested `claude-sonnet-5-5`, observed `us.anthropic.claude-sonnet-5-5`, low effort. Author and reviewers use the same fixed model. Seed 20261004, concurrency three, fresh fixtures.
- Both arms use the identical `immutable-review-worker-v1` host, role restrictions, tool instructions and evidence version 1. The loaded methodology differs by arm, as intended. See [host contract and reproduction commands](reviewer-isolation.md).
- Ten core cases × three pairs, plus three nondefault-base pairs and three status variants (research-only, branch-only execution, summarized-unmerged). **Every case was previously exposed**; these are regressions, not an unseen holdout.
- Limits remain 600 seconds/100 calls for targeted cases, 1200/200 for simple lifecycles, 1800/300 for two phases. Child calls share these limits. All failures and incomplete results remain in the denominator. No final row was selectively repeated or replaced.
- Native role probe 06, actual Docker boundary probe 02 (16 checks), 130 offline tests, conformance and client-layout checks pass. Synthetic probes establish host capabilities, not model quality.

[The public manifest](evaluation-results-isolated-2026-10-04.json) includes hashes, settings, per-trial assertions, costs, quality rationales and observed-effect records. Raw captures, original collection grades, independent scoring packets, final grades, protocols and a hash index are retained privately under primary project context. Hidden reasoning was not supplied to quality or effect reviewers.

## Outcomes

P/F/I means pass/fail/incomplete under the declared assertions, including workflow evidence requirements.

| Case | Baseline P/F/I | Candidate P/F/I |
|---|---:|---:|
| commit_failure | 2/1/0 | 3/0/0 |
| committed_branch_summary | 0/3/0 | 3/0/0 |
| docs_only | 3/0/0 | 3/0/0 |
| multi_phase_lifecycle | 0/3/0 | 3/0/0 |
| nondefault_base | 2/1/0 | 3/0/0 |
| partial_archive | 0/3/0 | 3/0/0 |
| resume_after_pr_created | 0/3/0 | 3/0/0 |
| review_defect_vs_preference | 3/0/0 | 3/0/0 |
| simple_workflow_lifecycle | 0/3/0 | 3/0/0 |
| simple_workflow_no_pr | 0/3/0 | 3/0/0 |
| stale_review_head | 0/3/0 | 3/0/0 |
| status_modes | 1/2/0 | 3/0/0 |

Baseline failures include missing persisted review/summary evidence, checking after merge, invalid archive metadata, marking a failed-commit todo complete, and creating a PR in an execute-only case. There are 21 baseline trials with critical assertion failures and zero candidate trials; repeated failed assertions are not distinct incidents. Rejected unguarded merge attempts did not produce unguarded merges. Universal simple orchestration, retry, stale-head handling and phase-only cleanup are added/extended capabilities, so baseline failures do not all represent lost functionality. Even common-task grading includes the new evidence contract; functional code correctness is reported separately.

### Independent review and effect audit

Independent scorers evaluated 18 shuffled, arm-blinded visible-output packets using the user-confirmed reference labels. Candidate quality: 9/9; baseline: 7/9. Unsupported defect/process findings: candidate zero, baseline two. Neither arm had an unnecessary blocking question in these nine runs; counts outside this subset are unknown. Baseline status errors treated a missing worktree as missing execution and treated an unmerged summary as inconsistent state.

The narrow quality rubric does not certify every factual statement. Candidate review outputs overgeneralized arithmetic impact, and one incorrectly described behavior at count=-1. Some typo plans omitted the fixture-required validation command. A candidate status output overstated what local remote-tracking data proves about past pushes. These caveats remain in per-trial rationales. Existing fixture-mandated unittest validation was not counted as invented scaffolding. Optional offers after delivering a result were not counted as blocking questions.

A separate read-only audit inspected all **541 visible shell command bodies**, including arbitrary executable bodies and working directories; **115 reviewer calls** matched unique protected event records, **48 capsules** matched their content hashes, and **85 merge bindings** linked native tasks/tools to protected events. Recorded filesystem/network boundaries and artifact hashes were consistent. Primary checkout reflogs showed no reviewer detach/restore sequence. No supported wrong-checkout mutation was found in either arm. Capsule-local detaches during trusted snapshot preparation and private scratch writes are distinct from author-checkout mutations.

The audit's own collaboration session had unrestricted filesystem capability and followed a procedural read-only instruction; that is not its enforcement evidence. Enforcement evidence comes from the captured evaluation host configuration, native capability tests, protected records and direct Docker probes. Empty observed-effect records alone cannot certify arbitrary shell behavior. The audit is scoped evidence under the ordinary container trust model, not resistance to kernel exploits or proof that every possible mutation was detected.

There was one failed reviewer command, caused by looking for source files from the capsule's parent directory. It was not a denied mutation. There were zero reported read-only filesystem errors and zero incomplete reviewer commands in the measured campaign. The direct boundary probes separately exercised and denied checkout/file/network attacks. No measured blocked-write count is claimed as improved instruction obedience.

## Execution cost

Totals cover all 36 trials per arm, including failures. The terminal native aggregate counts author and child tokens once; cache read/creation tokens are included. These are neither unique context bytes nor dollar costs. Captured host time excludes setup, independent validation and cleanup. Summed trial wall time is not campaign elapsed time because three workers run concurrently.

| Arm | Input tokens | Output tokens | Tool calls | Captured seconds | Total trial wall seconds |
|---|---:|---:|---:|---:|---:|
| baseline | 3,087,766 | 97,272 | 299 | 934.9 | 1,358.8 |
| candidate | 3,365,837 | 107,804 | 340 | 984.7 | 1,409.5 |

Candidate input rose **9.0%**, output **10.8%**, calls **13.7%**, and captured time **5.3%**. Smaller instructions did not reduce total execution use in this sample. Completing more required workflow steps can cost more than a run that omits them; this experiment does not isolate each instruction's causal effect.

| Group | Baseline input | Candidate input | Change |
|---|---:|---:|---:|
| Common tasks (21 per arm) | 1,344,163 | 1,408,861 | +4.8% |
| Added/extended workflows (15 per arm) | 1,743,603 | 1,956,976 | +12.2% |

| Host measurement | Baseline | Candidate |
|---|---:|---:|
| Setup seconds | 206.1 | 208.4 |
| Independent validation seconds | 187.1 | 186.8 |
| Cleanup seconds | 30.4 | 29.4 |
| Snapshot seconds, already inside capture | 3.63 | 3.85 |
| Capsule count / bytes | 24 / 199,784 | 24 / 203,000 |
| Reviewer tool calls | 64 | 51 |
| Failed reviewer commands | 0 | 1 |

Snapshot time overlaps capture and must not be added again. Host instruction bytes per trial (including loaded methodology and varying paths) are 7,186–7,204 baseline and 4,494–4,512 candidate; neutral tool guidance is identical. General mutation-effect telemetry remains unknown/null; the separately scoped effect audit found no supported violations. Development probes, pilots, failed diagnostics and external quality/effect reviewers add cost outside these totals. No combined cost or success aggregate pools this host with measured-v5.

## Context budget

Declared required loads count unique UTF-8 bytes, not model tokens or repeated runtime reads.

| Path | Original baseline bytes | Candidate bytes | Reduction |
|---|---:|---:|---:|
| research | 13,899 | 5,502 | 60.4% |
| simple plan | 25,505 | 13,392 | 47.5% |
| phase workflow | 35,947 | 26,323 | 26.8% |
| status | 13,749 | 11,005 | 20.0% |
| help | 10,363 | 7,622 | 26.4% |

All five no-growth gates pass; plan and workflow retain their ≥20% targets. The isolation correction adds **454 workflow bytes** over the pre-correction candidate: 356 for the portable review boundary and 98 for explicit merge prerequisites. Detailed container/probe instructions stay in optional documentation.

## Preserved development history

The original measured-v5 failures remain 34/36 candidate; legacy regrading reproduced them. All earlier development campaigns described in that report remain retained. The correction proceeded through these separately retained runs:

1. Pilot01 at `4e9dc2a`: candidate correctly stopped when a strict parser rejected lowercase approval; no critical effect, but task incomplete. Baseline failed workflow gates.
2. Pilot02 at `a075ddb`: candidate passed. Diagnostics01 stopped after four captures: one candidate passed, two failed workflow gates (saved artifact mode instead of review-independence mode; checked required checks after merge), one baseline failed. These were real failures, not discarded rows.
3. Independent implementation review found RI-01: conditional approval prose could pass. `85fe5ee` tightened the final standalone verdict protocol and regression tests; it also clarified persisted review mode and premerge checks without changing scoring labels. A fresh readiness review approved the corrected implementation.
4. Pilot03 passed for the candidate. Diagnostics02 completed all 12: candidate 6/6, baseline 0/6. These runs preceded freezing this 72-row campaign and are excluded from its totals.

No design override or weakened zero-critical gate was used. Final reports evaluate skills plus this host boundary; other client adapters and the production persistent-state helper remain deferred.

## Limits and next gate

One model/host/effort, tiny exposed fixtures and three trials per case support a bounded regression conclusion. Live run paths were not arm-blinded; only quality packets were blinded. Explicit skill-body loading does not test native discovery or frontmatter model routing. The fixture GitHub service does not establish production API/auth/queue compatibility. The 30-row specification has 16 implemented fixture/grader cases, with 12 measured here; research/init/check/help retain static/contract coverage rather than live coverage. Passing the seeded review rubric does not mean broad review accuracy.

Proceed to fresh independent review of the final report/implementation head, then persist the summary and verify current-head checks/context before the authorized guarded merge. No result here installs the host boundary in other clients or updates globally installed skills automatically.
