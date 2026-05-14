"""
tools/llmfit_tool.py — Agent Zero tool for hardware-aware model management.

The agent calls this tool with a JSON tool_call like:
{
    "tool_name": "llmfit",
    "tool_args": {
        "action": "recommend",
        "use_case": "coding",
        "limit": 3
    }
}

Actions:
  system     — detect hardware (CPU, RAM, GPU, VRAM)
  recommend  — get top N models for a use case
  info       — detailed info about a specific model
  list       — list running models in the a0_lmm_router fleet
  download   — delegate to a0_lmm_router fleet
  delete     — disabled local GGUF deletion
  bench      — live inference benchmark against a slot
"""
try:
    from python.helpers.tool import Tool, Response
    from usr.plugins.llmfit_advisor.helpers.llmfit import (
        system_specs,
        recommend,
        model_info,
        list_local_models,
        download_model,
        delete_model,
        dependency_versions,
        bench,
    )
except ImportError:
    import sys, os
    _here = os.path.dirname(os.path.abspath(__file__))
    _plugin_root = os.path.dirname(_here)
    if _plugin_root not in sys.path:
        sys.path.insert(0, _plugin_root)
    from python.helpers.tool import Tool, Response
    from helpers.llmfit import (
        system_specs,
        recommend,
        model_info,
        list_local_models,
        download_model,
        delete_model,
        dependency_versions,
        bench,
    )

import json


class LlmfitTool(Tool):
    async def execute(self, **kwargs):
        action = self.args.get("action", "").lower()

        if action == "system":
            data = system_specs()
            return Response(
                message=_format("Hardware specs", data),
                break_loop=False,
            )

        elif action == "recommend":
            use_case = self.args.get("use_case", "general")
            limit = int(self.args.get("limit", 5))
            data = recommend(use_case=use_case, limit=limit)
            return Response(
                message=_format(f"Top {limit} models for '{use_case}'", data),
                break_loop=False,
            )

        elif action == "info":
            name = self.args.get("model_name", "")
            if not name:
                return Response(message="Error: model_name is required", break_loop=False)
            data = model_info(name)
            return Response(
                message=_format(f"Info for {name}", data),
                break_loop=False,
            )

        elif action == "list":
            models = list_local_models()
            return Response(
                message=_format("Fleet model listing", models),
                break_loop=False,
            )

        elif action == "download":
            hf_repo = self.args.get("hf_repo", "")
            filename = self.args.get("filename", "")
            result = download_model(hf_repo, filename)
            return Response(
                message=_format("Download model via a0_lmm_router", result),
                break_loop=False,
            )

        elif action == "delete":
            filename = self.args.get("filename", "")
            result = delete_model(filename)
            return Response(
                message=_format("Local GGUF deletion disabled", result),
                break_loop=False,
            )

        elif action == "versions":
            data = dependency_versions()
            return Response(
                message=_format("Dependency versions", data),
                break_loop=False,
            )

        elif action == "bench":
            model_name = self.args.get("model_name", "")
            endpoint = self.args.get("endpoint", "")
            duration = int(self.args.get("duration", 60))
            if not model_name:
                return Response(message="Error: model_name is required for bench", break_loop=False)
            data = bench(model_name=model_name, endpoint=endpoint, duration=duration)
            return Response(
                message=_format(f"Benchmark for {model_name}", data),
                break_loop=False,
            )

        else:
            return Response(
                message=(
                    f"Unknown action: '{action}'. "
                    "Valid actions: system, recommend, info, list, download, delete, bench"
                ),
                break_loop=False,
            )


def _format(title: str, data: dict | list) -> str:
    """Format JSON data for agent consumption."""
    return f"{title}:\n```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```"
