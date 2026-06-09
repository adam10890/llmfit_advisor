# DOX contract - llmfit_advisor/helpers

## Purpose

Hardware detection, recommendation, and router-adapter helper code.

## Ownership

- Keep probing, scoring, and formatting responsibilities separated.
- Do not write model downloads, benchmark outputs, or host inventory snapshots
  into this directory.

## Local Contracts

- Missing hardware facts must degrade into explicit unknown values.
- Router integration must stay optional and best-effort.

## Work Guidance

- Prefer pure helper functions where possible so tools can stay thin.

## Verification

- Run `python -m py_compile` on touched helper files.

## Child DOX Index

No child AGENTS.md files yet.
