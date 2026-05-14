## Tool: llmfit
Hardware-aware local LLM model manager. Use this tool to understand what models
can run on your hardware, manage your local GGUF model library, and make
informed decisions about which model to load for a given task.

**When to use:**
- You need to know your hardware specs (GPU, VRAM, RAM)
- You need to choose which local model to run
- You need to download or manage GGUF model files
- Someone asks "what models can I run?" or "recommend a coding model"

**Actions:**

### system
Detect hardware. No arguments needed.
```json
{ "tool_name": "llmfit", "tool_args": { "action": "system" } }
```

### recommend
Get ranked model recommendations.
- `use_case`: general | coding | reasoning | chat | multimodal | embedding
- `limit`: number of results (default 5)
```json
{ "tool_name": "llmfit", "tool_args": { "action": "recommend", "use_case": "coding", "limit": 3 } }
```

### info
Get details about a specific model.
```json
{ "tool_name": "llmfit", "tool_args": { "action": "info", "model_name": "Mistral-7B" } }
```

### list
List models known to the a0_lmm_router fleet (running slots + roles).
```json
{ "tool_name": "llmfit", "tool_args": { "action": "list" } }
```

### download
Download a GGUF via the a0_lmm_router fleet (delegates to huggingface-cli).
```json
{ "tool_name": "llmfit", "tool_args": { "action": "download", "hf_repo": "TheBloke/Mistral-7B-v0.1-GGUF", "filename": "mistral-7b-v0.1.Q6_K.gguf" } }
```

### delete
Remove a local GGUF file.
```json
{ "tool_name": "llmfit", "tool_args": { "action": "delete", "filename": "mistral-7b-v0.1.Q6_K.gguf" } }
```

### versions
Check installed versions of all dependencies (llmfit, llama-server, nvidia driver).
Useful for diagnosing issues or deciding when to update.
```json
{ "tool_name": "llmfit", "tool_args": { "action": "versions" } }
```

### bench
Live inference benchmark against a running llama.cpp slot.
- `model_name`: required model identifier
- `endpoint`: optional http://host:port/v1/completions URL
- `duration`: seconds to run (default 60)
```json
{ "tool_name": "llmfit", "tool_args": { "action": "bench", "model_name": "Mistral-7B", "endpoint": "http://host.docker.internal:8080", "duration": 60 } }
```

**Updating dependencies:**
- llmfit: `curl -fsSL https://llmfit.axjns.dev/install.sh | sh`
- llama.cpp: see README.md in the plugin folder for full instructions
- Neither binary persists across container rebuilds — reinstall after `docker pull`
