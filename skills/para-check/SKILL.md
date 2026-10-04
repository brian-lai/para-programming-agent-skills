---
name: para-check
description: Decision helper to determine if PARA workflow should be used for a given request. Triages tasks into PARA-worthy vs direct-answer categories.
model: haiku
effort: low
---

Triage the request against the project's branch/PR policy.

```text
para-check "<request>"
```

- Tracked code changes, features, bug fixes, configuration or documentation edits: **USE PARA WORKFLOW**. Use the `para-plan` skill, reusing an active applicable plan.
- Read-only questions, navigation, explanations or state inspection: **SKIP PARA** and answer directly.
- Research/plan/progress/summary artifacts in primary context do not recursively require another plan. Continue the active workflow.
- Unclear intent: inspect available context, then ask only if whether to change files remains consequentially ambiguous.

Return the verdict, one-sentence reason and next action. Do not start implementation from a triage request.
