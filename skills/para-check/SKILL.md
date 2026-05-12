---
name: para-check
description: Decision helper to determine if PARA workflow should be used for a given request. Triages tasks into PARA-worthy vs direct-answer categories.
model: haiku
effort: low
---

Decision helper to determine if PARA workflow should be used for a given request.

## Usage

```
/para-check "Add user authentication to the API"
/para-check "Where is the auth middleware defined?"
```

## Decision Logic

```
Does this request require code/file changes?
|- YES -> USE PARA WORKFLOW
|        Next: Run /para-plan to create an implementation plan.
`- NO  -> SKIP PARA
         |- Read-only project question -> Direct answer with file references
         |- navigation request -> Point to relevant files or commands
         |- explanations -> Explain directly
         `- General question -> Standard response
```

## Use PARA Workflow For

- features or user-facing behavior changes
- bug fixes
- refactoring
- config changes, migrations, tests, or documentation edits
- architecture decisions or complex debugging that may lead to code changes

## Skip PARA For

- Read-only questions about the codebase
- file or symbol navigation
- explanations of existing behavior
- general informational questions
- commands that only inspect state and do not edit files

## Output Format

Display a short verdict with reasoning:

```
PARA Workflow Check

Request: "Add user authentication to the API"

USE PARA WORKFLOW

Reason: This request requires code changes and file modifications.
Next: Run /para-plan to create an implementation plan.
```

For skip cases, replace the verdict with `SKIP PARA` and provide the direct answer or inspection path.
