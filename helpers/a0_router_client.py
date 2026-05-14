"""
a0_router_client.py — lightweight HTTP client to a0_lmm_router APIs.

Used by llmfit_advisor to delegate list/download/delete/bench operations
to the fleet managed by a0_lmm_router instead of doing them locally.

Env overrides:
  A0_LMM_ROUTER_URL  — base URL of the Agent Zero web server
                       (default: http://127.0.0.1:5001)
"""
import json
import os
import urllib.request
from typing import Any, Dict

ROUTER_BASE = os.environ.get("A0_LMM_ROUTER_URL", "http://127.0.0.1:5001")


def _router_api(path: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """POST JSON to /plugins/a0_lmm_router/<path> and return parsed dict."""
    url = f"{ROUTER_BASE}/plugins/a0_lmm_router/{path}"
    try:
        data = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        return {"ok": False, "error": str(e), "_router_unreachable": True}


def fleet_status() -> Dict[str, Any]:
    """Return running slot status from the router."""
    return _router_api("llamacpp_status", {})


def compute_snapshot() -> Dict[str, Any]:
    """Return GPU/CPU/LMM snapshot from the router."""
    return _router_api("lmm_compute_stats", {})


def install_model(repo_id: str, filename: str) -> Dict[str, Any]:
    """Ask the router to download a GGUF model via huggingface-cli."""
    return _router_api("lmm_model_install", {"repo_id": repo_id, "filename": filename})


def model_recommendations(role: str | None = None) -> Dict[str, Any]:
    """Get hardware-aware recommendations from the router catalog."""
    payload = {}
    if role:
        payload["role"] = role
    return _router_api("lmm_model_recommend", payload)
