# LLMFit Advisor — Agent Zero Plugin

Hardware-aware local LLM model manager for Agent Zero.

Uses [llmfit](https://github.com/AlexsJones/llmfit) to detect your GPU/RAM, score 497+ models, and recommend the best ones for your hardware. Integrates with a0_lmm_router for fleet-wide model management — list, download, and benchmark models against running llama.cpp slots.

## What it does

The agent gets a `llmfit` tool with 7 actions:

| Action | What | LLM needed? |
|---|---|---|
| `system` | Detect CPU, RAM, GPU, VRAM | No |
| `recommend` | Top N models for a use case (enriched with fleet status) | No |
| `info` | Details about a specific model | No |
| `list` | Show running slots from a0_lmm_router fleet | No |
| `download` | Download GGUF via a0_lmm_router (delegated) | No |
| `delete` | Remove a local GGUF | No |
| `bench` | Live inference benchmark against a slot (v0.9.19+) | No |

**No LLM is used by this plugin.** It's a pure CLI/filesystem/HTTP tool.

## Setup

### 1. Docker volume for models

```yaml
# docker-compose.yml or docker run
volumes:
  - /path/on/host/models:/a0/usr/models
```

This directory persists across container restarts and updates.

### 2. GPU passthrough

For llmfit to detect your GPU inside Docker:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - capabilities: [gpu]
```

Or with `docker run`:
```bash
docker run --gpus all -v /path/models:/a0/usr/models ...
```

### 3. Install the plugin

Copy to `usr/plugins/` inside your Agent Zero:

```bash
cp -r llmfit_advisor /path/to/agent-zero/usr/plugins/
```

The `hooks.py` will auto-install the llmfit binary in a background thread on first load (non-blocking for A0 v1.10+).

## Integration with a0_lmm_router

When a0_lmm_router is active on the same Agent Zero instance, this plugin delegates:

- `list` → queries `/plugins/a0_lmm_router/llamacpp_status`
- `download` → delegates to `/plugins/a0_lmm_router/lmm_model_install`
- `recommend` → enriches each model with `fleet_status: running/available`

Set `A0_LMM_ROUTER_URL` if the router is on a different host.

## Example agent conversation

> **You:** What models can I run for coding?
>
> **Agent:** Let me check your hardware and find the best coding models.
> *(calls llmfit tool: system → recommend --use-case coding)*
>
> > Your RTX 4090 (24GB VRAM) can run these coding models optimally:
> > 1. Qwen2.5-Coder-32B at Q5_K — 22.1 GB, ~28 tok/s (fleet: running)
> > 2. DeepSeek-Coder-V2-Lite at Q6_K — 18.4 GB, ~35 tok/s
> > ...
>
> Want me to download one?

## Dependency Map & Update Guide

This plugin depends on two external binaries. Neither is pinned to a specific version.

| Dependency | What | Installed by | Binary location | Upstream |
|---|---|---|---|---|
| **llmfit** | Model scoring & HW detection | `hooks.py` (background) | `/usr/local/bin/llmfit` | [AlexsJones/llmfit](https://github.com/AlexsJones/llmfit) |
| **llama.cpp** | GGUF inference server | You (manual) | `/usr/local/bin/llama-server` | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) |

### Updating llmfit

```bash
docker exec -it <container> sh -c \
  "curl -fsSL https://llmfit.axjns.dev/install.sh | sh"
```

**New in v0.9.19:** `llmfit bench` for live inference benchmarking.

### Updating this plugin

```bash
rm -rf /path/to/agent-zero/usr/plugins/llmfit_advisor
cp -r llmfit_advisor /path/to/agent-zero/usr/plugins/
```

Agent Zero hot-reloads plugins — no restart needed.

## License

MIT
