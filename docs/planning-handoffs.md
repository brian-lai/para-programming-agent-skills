# Planning for a fresh executor

Use a stronger reasoning configuration for research/planning and a cheaper executor through your host's model settings. PARA skills describe responsibilities and evidence; they do not select providers, model names or effort. A fresh executor needs the selected plan, relevant research, project guidance and current repository access, not the planner's conversation.

## What to carry forward

Research resolves consequential questions and records verified paths/symbols, nearby patterns, decisions with rationale, material prerequisites and freshness triggers. Plans carry the actionable subset. Link background evidence with a reason to consult it; avoid copying investigation transcripts.

A nontrivial step identifies the intended behavior and edge cases, where to change it, dependencies, validation command/cwd/expected result and mismatches requiring investigation. Label proposed paths and assumed tool availability. A typo fix can simply identify the file, replacement and manual diff check; it needs no environment inventory or architecture section.

Example using the evaluation calculator fixture:

> Correct `calculator.py:ratio` to divide by `count`, preserving its existing `ValueError` for zero. `examples.py:mean` shows the exception convention. Check positive and negative counts and zero; run `python3 -m unittest discover -p "test_*.py"` from the execution root. Python 3 availability is assumed until checked. If the symbol has moved, resolve its current location before editing; preserve the current API.

Verify the actual source before applying an example. A location is evidence about a revision, not a guarantee that it remains current.

## Execution and review

Start with the next step and its shared constraints. Inspect named code and needed prerequisites; load background research for a missing fact. Reuse decisions until a contradiction, missing contract or unexplained validation failure warrants focused investigation. Record resolved gaps once for later steps.

Repeating an unsuccessful repair/search requires new evidence or a changed hypothesis. Otherwise preserve the last verified state, failed action/result and unresolved fact. Continue independent work and return the blocked step to its caller for targeted investigation or consequential replanning. Direct execute does not independently launch a new lifecycle. Transient failures or pending CI can justify bounded waiting; rapid identical calls add no useful evidence.

Review asks whether a fresh executor can locate the change, understand required behavior, validate it and recognize a mismatch. Findings identify a concrete defect or missing contract. Approval with no blockers is valid; style preferences do not justify another round. Focus corrections on affected parts/interactions, while retaining fresh independent review and approval for the actual target. Merge checks, preserved evidence and archive verification remain mandatory.

## Reconcile existing global guidance

The installer preserves existing active global guidance. A symlinked skill update does not automatically update a customized `~/.agents/AGENTS.md`.

1. Identify the permanent checkout and actual skill locations loaded by the host; record the checkout revision.
2. Compare active guidance with `resources/AGENTS.md`, for example `diff -u ~/.agents/AGENTS.md resources/AGENTS.md` from that checkout. This only displays differences.
3. Reconcile obsolete PARA sections in a reviewable edit while retaining unrelated custom policy. Watch for fixed persona instructions, forced reread rounds, redundant questions and outdated cleanup rules. Do not replace the whole file blindly.
4. After an authorized edit, confirm that active guidance and loaded skill contracts agree. Follow the host's reload/discovery procedure when needed.

This repository change neither edits external guidance nor installs another host adapter. Model settings in historical evaluation reports remain reproducibility data.

## Efficiency evidence

Fewer static instruction bytes do not imply fewer runtime tokens. Compare successful completion, errors, actual calls/tokens/time and user interventions, retaining failed attempts. Generated planning, implementation, review, external waiting and lifecycle bookkeeping can contribute different costs. A small authored-plan pilot measures a limited handoff effect; genuinely generated plans and full auto completion require separate live evidence.
