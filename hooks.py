"""
hooks.py — Framework-level lifecycle hooks.
Runs in the Agent Zero framework venv (/opt/venv-a0 in Docker).

install() is called after the plugin is copied into place.
It defers the llmfit binary install to a background thread so it never
blocks A0 v1.10+ startup.  The first tool call will lazily re-try if the
binary is still missing.
"""
import subprocess
import logging
import threading

log = logging.getLogger("llmfit_advisor.hooks")


def install(**kwargs):
    """Called by Agent Zero after plugin installation.

    v1.10+ awaits preload hooks serially — any blocking I/O deadlocks the
    entire framework boot.  We only kick off a background thread here and
    return immediately.
    """
    if _binary_exists("llmfit"):
        log.info("[llmfit_advisor] llmfit already installed")
        _log_version()
        return

    log.info("[llmfit_advisor] llmfit not found; starting background install...")
    threading.Thread(target=_background_install, daemon=True).start()
    log.info(
        "[llmfit_advisor] llmfit will be installed in background. "
        "First tool call will block briefly if binary is still missing."
    )


def _background_install():
    """Try curl, then cargo.  Never raises — failures are logged only."""
    try:
        subprocess.run(
            ["sh", "-c", "curl -fsSL https://llmfit.axjns.dev/install.sh | sh"],
            check=True, timeout=120,
        )
        log.info("[llmfit_advisor] llmfit installed via curl")
        _log_version()
        return
    except Exception as e:
        log.warning(f"[llmfit_advisor] curl install failed: {e}")

    try:
        subprocess.run(
            ["cargo", "install", "llmfit"],
            check=True, timeout=300,
        )
        log.info("[llmfit_advisor] llmfit installed via cargo")
        _log_version()
    except Exception as e2:
        log.error(f"[llmfit_advisor] Failed to install llmfit: {e2}")
        log.error("[llmfit_advisor] Install manually: cargo install llmfit")


def _log_version():
    try:
        ver = subprocess.run(
            ["llmfit", "--version"], capture_output=True, text=True, timeout=5
        )
        log.info(f"[llmfit_advisor] llmfit version: {ver.stdout.strip()}")
    except Exception:
        pass


def _binary_exists(name: str) -> bool:
    try:
        subprocess.run(["which", name], capture_output=True, check=True)
        return True
    except Exception:
        return False
