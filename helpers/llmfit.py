"""
helpers/llmfit.py — Thin wrapper around the llmfit CLI.
All functions return parsed Python dicts from JSON output.
No LLM involved — pure subprocess + JSON.
"""
from __future__ import annotations
import json
import subprocess
import logging

log = logging.getLogger("llmfit_advisor")


def _get_config() -> dict:
    """Load plugin config. Works both with and without Agent Zero imports."""
    try:
        from helpers.plugins import get_plugin_config
        return get_plugin_config("llmfit_advisor") or {}
    except ImportError:
        return {}


def _llmfit_bin() -> str:
    cfg = _get_config()
    return cfg.get("llmfit_bin", "llmfit")


def _models_dir() -> str:
    cfg = _get_config()
    return cfg.get("models_dir", "")


def _gpu_override_args() -> list[str]:
    cfg = _get_config()
    override = cfg.get("gpu_memory_override", "")
    if override:
        return [f"--memory={override}"]
    return []


def _ensure_llmfit_binary():
    """Lazy install: if llmfit is missing, try once more in foreground."""
    try:
        subprocess.run([_llmfit_bin(), "--version"], capture_output=True, check=True, timeout=5)
    except Exception:
        log.info("[llmfit_advisor] llmfit missing; attempting foreground install...")
        try:
            subprocess.run(
                ["sh", "-c", "curl -fsSL https://llmfit.axjns.dev/install.sh | sh"],
                check=True, timeout=120, capture_output=True,
            )
        except Exception as e:
            log.warning(f"[llmfit_advisor] foreground install failed: {e}")


def system_specs() -> dict:
    """Detect hardware: CPU, RAM, GPU, VRAM, backend."""
    _ensure_llmfit_binary()
    try:
        result = subprocess.run(
            [_llmfit_bin(), "--json", "system"] + _gpu_override_args(),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        log.error(f"llmfit system failed: {e}")
    return {"error": "Could not detect hardware. Is llmfit installed?"}


def recommend(use_case: str = "general", limit: int = 5, enrich_fleet: bool = True) -> dict:
    """Get ranked model recommendations for this hardware.

    If enrich_fleet is True and a0_lmm_router is reachable, tag each model
    with fleet_status (running / available / missing).
    """
    _ensure_llmfit_binary()
    cmd = [
        _llmfit_bin(), "recommend", "--json",
        "--use-case", use_case,
        "--limit", str(limit),
    ] + _gpu_override_args()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if enrich_fleet:
                data = _enrich_with_fleet(data)
            return data
    except Exception as e:
        log.error(f"llmfit recommend failed: {e}")
    return {"error": "llmfit recommend failed"}


def _enrich_with_fleet(data: dict) -> dict:
    """Tag models in recommend output with fleet_status if a0_lmm_router is up."""
    try:
        from usr.plugins.llmfit_advisor.helpers.a0_router_client import fleet_status
        fleet = fleet_status()
        if not fleet.get("ok"):
            return data
        running = {s.get("model_id") for s in fleet.get("slots", []) if s.get("running")}
        for m in data.get("models", []):
            m_name = m.get("name", "")
            m["fleet_status"] = "running" if m_name in running else "available"
    except Exception:
        pass
    return data


def model_info(model_name: str) -> dict:
    """Get detailed info about a specific model."""
    try:
        result = subprocess.run(
            [_llmfit_bin(), "info", model_name, "--json"] + _gpu_override_args(),
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        log.error(f"llmfit info failed: {e}")
    return {"error": f"Could not get info for {model_name}"}


def list_local_models() -> list[dict]:
    """Return models known to the a0_lmm_router fleet."""
    try:
        from usr.plugins.llmfit_advisor.helpers.a0_router_client import fleet_status
        fleet = fleet_status()
        if fleet.get("ok") and "slots" in fleet:
            return [
                {
                    "name": s.get("model_id"),
                    "role": s.get("role"),
                    "running": s.get("running"),
                    "healthy": s.get("healthy"),
                    "port": s.get("port"),
                }
                for s in fleet.get("slots", [])
            ]
    except Exception as e:
        log.debug(f"list_local_models fleet query failed: {e}")
    return []


def download_model(hf_repo: str, filename: str) -> dict:
    """Delegate to a0_lmm_router lmm_model_install if available."""
    try:
        from usr.plugins.llmfit_advisor.helpers.a0_router_client import install_model
        result = install_model(repo_id=hf_repo, filename=filename)
        if not result.get("_router_unreachable"):
            return result
    except Exception as e:
        log.debug(f"download_model router delegation failed: {e}")
    return {
        "status": "disabled",
        "error": "a0_lmm_router unreachable and local GGUF downloads inside Agent Zero are disabled.",
    }


def delete_model(filename: str) -> dict:
    return {
        "status": "disabled",
        "error": "Local GGUF deletion inside Agent Zero is disabled. Manage models in the external LMM fleet.",
    }


def bench(model_name: str, endpoint: str = "", duration: int = 60) -> dict:
    """Run llmfit bench against a live endpoint (e.g. an a0_lmm_router slot).

    If endpoint is empty, llmfit will pick its own default or fail gracefully.
    """
    _ensure_llmfit_binary()
    cmd = [_llmfit_bin(), "bench", "--json", model_name]
    if endpoint:
        cmd += ["--endpoint", endpoint]
    cmd += ["--duration", str(duration)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr.strip() or "bench command failed"}
    except Exception as e:
        log.error(f"llmfit bench failed: {e}")
    return {"error": "bench failed"}


def dependency_versions() -> dict:
    """
    Check installed versions of all dependencies.
    Useful for debugging and knowing when to update.
    """
    versions = {}

    for binary, flag in [("llmfit", "--version"), ("llama-server", "--version")]:
        try:
            result = subprocess.run(
                [binary, flag], capture_output=True, text=True, timeout=5
            )
            versions[binary] = {
                "installed": True,
                "version": result.stdout.strip() or result.stderr.strip(),
            }
        except FileNotFoundError:
            versions[binary] = {"installed": False, "version": None}
        except Exception as e:
            versions[binary] = {"installed": False, "error": str(e)}

    # Check nvidia-smi for GPU driver version
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        )
        versions["nvidia_driver"] = result.stdout.strip()
    except Exception:
        versions["nvidia_driver"] = "not detected"

    return versions
