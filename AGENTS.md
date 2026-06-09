# DOX contract - llmfit_advisor

## Purpose

Hardware-aware local model advisor for Agent Zero. It detects host CPU/RAM/GPU,
recommends GGUF models, reports model-fit guidance, and delegates fleet-aware
download/list/benchmark actions to `a0_lmm_router` when available.

## Ownership

- This folder is plugin source, not runtime model storage.
- Hardware probing and model recommendation logic belongs in `helpers/`.
- Agent-facing actions belong in `tools/`; tool prompts belong in `prompts/`.
- Do not vendor large model catalogs, downloaded GGUFs, benchmark artifacts, or
  runtime cache files into plugin source.

## Local Contracts

- `plugin.yaml:name` must stay `llmfit_advisor`.
- Keep `llmfit` behavior optional and failure-tolerant; missing hardware facts
  should degrade into a clear report rather than breaking the agent loop.
- Router delegation must remain best-effort. If `a0_lmm_router` is unavailable,
  advisor actions should explain the missing integration instead of importing
  router internals blindly.
- Keep model-fit output compact enough for agent use; long model inventories
  belong behind explicit list/detail actions.

## Work Guidance

- Inspect `README.md` and `default_config.yaml` before changing tool behavior.
- Keep hardware detection separate from recommendation formatting.
- Do not assume a Windows/RTX-4090 host unless the config or detected hardware
  says so.

## Verification

- Run `python -m py_compile` on touched Python files.
- For prompt/tool changes, inspect that `prompts/agent.system.tool.*.md` names
  match the exposed tool names.

## Child DOX Index

- `helpers/AGENTS.md` — hardware detection, recommendation, and router adapter
  helper contracts.
- `tools/AGENTS.md` — agent-facing `llmfit` actions and response shape.
- `prompts/AGENTS.md` — tool prompt guidance and prompt/tool name alignment.
- `docs/AGENTS.md` — user-facing runbooks and durable design notes.
