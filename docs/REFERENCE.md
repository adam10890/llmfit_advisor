# llmfit_advisor — Reference

**Version:** 0.4.0 | Agent Zero v1.15–v1.17

## Overview

Hardware-aware local LLM model manager for Agent Zero. Detects your GPU/VRAM, scores 497+ GGUF models against your hardware, and recommends the best fit. Integrates with `a0_lmm_router` for fleet management.

**No LLM is used.** This is a pure CLI/HTTP tool.

## Requirements

- `llmfit` binary — auto-installed by `hooks.py` on first activation
- Docker with GPU passthrough for VRAM detection: `--gpus all`
- (Optional) `a0_lmm_router` for fleet listing + model downloads

## Installation

```bash
docker cp ./llmfit_advisor <container>:/a0/usr/plugins/llmfit_advisor
```

`hooks.py` installs the `llmfit` binary in a background thread — A0 does not block during installation.

## Tool API

Tool name: `llmfit`

### system — detect hardware
```json
{"tool_name":"llmfit","tool_args":{"action":"system"}}
```
Returns: CPU model, RAM (GB), GPU model, VRAM (GB).

### recommend — top models for a use case
```json
{
  "tool_name": "llmfit",
  "tool_args": {
    "action": "recommend",
    "use_case": "coding",
    "limit": 5
  }
}
```
Use cases: `coding`, `chat`, `reasoning`, `multilingual`, `general`

With `a0_lmm_router` active, each result includes `fleet_status: running|available`.

### info — model details
```json
{"tool_name":"llmfit","tool_args":{"action":"info","model_name":"Qwen2.5-Coder-32B-Q5_K_M"}}
```

### list — running fleet slots
```json
{"tool_name":"llmfit","tool_args":{"action":"list"}}
```
Requires `a0_lmm_router`.

### download — download a GGUF
```json
{
  "tool_name": "llmfit",
  "tool_args": {
    "action": "download",
    "hf_repo": "bartowski/Qwen2.5-Coder-32B-Instruct-GGUF",
    "filename": "Qwen2.5-Coder-32B-Instruct-Q5_K_M.gguf"
  }
}
```
Delegated to `a0_lmm_router`.

### bench — live inference benchmark
```json
{
  "tool_name": "llmfit",
  "tool_args": {
    "action": "bench",
    "model_name": "Qwen2.5-Coder-32B-Q5_K_M",
    "endpoint": "http://localhost:8080",
    "duration": 60
  }
}
```
Requires llmfit v0.9.19+.

### versions
```json
{"tool_name":"llmfit","tool_args":{"action":"versions"}}
```

## GPU passthrough (Docker)

```yaml
# docker-compose.yml
services:
  agent-zero:
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
```

Or: `docker run --gpus all ...`

## Updating llmfit

```bash
docker exec -it <container> sh -c \
  "curl -fsSL https://llmfit.axjns.dev/install.sh | sh"
```

## Integration with a0_lmm_router

Set `A0_LMM_ROUTER_URL` env var if the router runs on a different host (default: auto-detected on the same instance).
