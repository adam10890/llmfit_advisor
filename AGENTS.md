# AGENTS.md — llmfit_advisor

**Version:** 0.4.0 | **Target:** Agent Zero v1.15–v1.17

## What this plugin does

Hardware-aware local LLM model manager. Uses the `llmfit` CLI to detect GPU/VRAM/RAM, score 497+ GGUF models, and recommend the best fits for the current hardware. Integrates with `a0_lmm_router` for fleet-wide download and listing. **No LLM is used by this plugin** — it is a pure CLI/filesystem/HTTP tool.

## Key files

| Path | Role |
|---|---|
| `plugin.yaml` | Manifest — section: `developer`, no per-project/agent config |
| `tools/llmfit_tool.py` | `LlmfitTool(Tool)` — 8 actions |
| `helpers/llmfit.py` | CLI wrapper — `system_specs`, `recommend`, `model_info`, `bench`, … |
| `hooks.py` | `install(**kwargs)` — background-thread binary install (non-blocking) |
| `prompts/` | Agent tool guidance |

## Tool: `llmfit`

| Action | Key args | Router needed? | Notes |
|---|---|---|---|
| `system` | — | No | CPU, RAM, GPU, VRAM detection |
| `recommend` | `use_case`, `limit` | No | Top N models scored for hardware |
| `info` | `model_name` | No | Single model details |
| `list` | — | Optional | Running fleet slots |
| `download` | `hf_repo`, `filename` | Yes | Delegates to a0_lmm_router |
| `delete` | `filename` | No | Currently disabled (safety) |
| `versions` | — | No | llmfit + llama.cpp version info |
| `bench` | `model_name`, `endpoint`, `duration` | Yes | Live inference benchmark |

## Binary install pattern

`hooks.py::install(**kwargs)` spawns a daemon thread that:
1. Tries `curl -fsSL https://llmfit.axjns.dev/install.sh | sh`
2. Falls back to `cargo install llmfit`
3. Never blocks A0 boot

The binary is checked on every tool call inside `helpers/llmfit.py`.

## a0_lmm_router delegation

When `a0_lmm_router` is active on the same instance:
- `list` → `GET /plugins/a0_lmm_router/llamacpp_status`
- `download` → `POST /plugins/a0_lmm_router/lmm_model_install`
- `recommend` enriches each result with `fleet_status: running|available`

Set `A0_LMM_ROUTER_URL` env var if the router is on a different host.

## How to add a new action

1. Add a helper function in `helpers/llmfit.py` wrapping the CLI command.
2. Add an `elif action == "my_action":` block in `LlmfitTool.execute()`.
3. Import the helper at the top of `tools/llmfit_tool.py`.

## Constraints

- `llmfit` binary must be in `PATH` — `hooks.py` installs it on first activation.
- Docker GPU passthrough is required for VRAM detection: `--gpus all`.
- `delete` action is intentionally disabled — prevents accidental model loss.
- No `uninstall` hook — the binary is left in place on plugin removal.
