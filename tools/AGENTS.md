# DOX contract - llmfit_advisor/tools

## Purpose

Agent-facing `llmfit` tool actions.

## Ownership

- Tools translate agent requests into helper calls and compact responses.
- Long inventories should require explicit list/detail actions.

## Local Contracts

- Keep action names aligned with `../README.md` and prompt guidance.
- Do not make router availability a hard requirement for local system/recommend
  actions.

## Work Guidance

- Route hardware and recommendation logic through `helpers/`.

## Verification

- Run `python -m py_compile` on touched tool files.
- Inspect matching prompt files when action names change.

## Child DOX Index

No child AGENTS.md files yet.
