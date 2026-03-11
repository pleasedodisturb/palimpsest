#!/usr/bin/env python3
"""Daily and hourly update runner for Palimpsest pipelines.

Orchestrates a sequence of sync, build, and publish steps with
error handling and run state tracking.

Usage:
    python daily_update_runner.py --mode daily
    python daily_update_runner.py --mode hourly

Environment:
    PAC_PYTHON       — Python binary to use (default: auto-discover)
    PAC_PROJECT_ROOT — Project root directory
    PAC_ARCHIVE_LOG  — Path to archive log markdown file
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
RUN_STATE_PATH = SCRIPT_DIR / ".run_state.json"


# ---------------------------------------------------------------------------
# Python binary discovery
# ---------------------------------------------------------------------------

def find_python():
    """Discover the best Python binary to use.

    Priority:
        1. PAC_PYTHON environment variable
        2. venv/bin/python in the scripts directory
        3. sys.executable as fallback

    Returns:
        str: Path to Python binary.
    """
    # 1. Environment variable
    env_python = os.environ.get("PAC_PYTHON")
    if env_python and shutil.which(env_python):
        return env_python

    # 2. Local venv
    venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)

    # 3. Fallback
    return sys.executable


# ---------------------------------------------------------------------------
# Step runner
# ---------------------------------------------------------------------------

def run_step(name, command, env=None, allow_fail=False):
    """Run a single pipeline step.

    Args:
        name: Human-readable step name.
        command: Command as a list of strings or shell string.
        env: Optional environment variables to add.
        allow_fail: If True, failure does not stop the pipeline.

    Returns:
        dict: Result with keys: name, success, duration, output, error.
    """
    print(f"\n--- Step: {name} ---")
    start = datetime.now(timezone.utc)

    run_env = dict(os.environ)
    if env:
        run_env.update(env)

    try:
        if isinstance(command, str):
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                env=run_env,
                timeout=300,
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=run_env,
                timeout=300,
            )

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        success = result.returncode == 0

        if success:
            print(f"  OK ({elapsed:.1f}s)")
        else:
            msg = f"  FAILED ({elapsed:.1f}s): {result.stderr.strip()[:200]}"
            print(msg)
            if not allow_fail:
                print(f"  Step '{name}' failed and allow_fail=False")

        return {
            "name": name,
            "success": success,
            "duration": elapsed,
            "output": result.stdout.strip()[:500],
            "error": result.stderr.strip()[:500] if not success else "",
        }

    except subprocess.TimeoutExpired:
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        print(f"  TIMEOUT ({elapsed:.1f}s)")
        return {
            "name": name,
            "success": False,
            "duration": elapsed,
            "output": "",
            "error": "Step timed out after 300s",
        }
    except Exception as e:
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        print(f"  ERROR: {e}")
        return {
            "name": name,
            "success": False,
            "duration": elapsed,
            "output": "",
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Pipeline definitions
# ---------------------------------------------------------------------------

def get_daily_steps(python_bin):
    """Return the full daily sync pipeline steps.

    Args:
        python_bin: Path to Python binary.

    Returns:
        list[tuple]: (name, command, env, allow_fail) tuples.
    """
    scripts = SCRIPT_DIR
    return [
        ("Preflight check", [python_bin, str(scripts / "core" / "preflight_check.py"), "--service", "all"], None, True),
        ("Google Drive sync", [python_bin, str(scripts / "sync" / "gdrive_sync.py")], None, True),
        ("Calendar sync", [python_bin, str(scripts / "sync" / "calendar_sync.py")], None, True),
        ("Build document registry", [python_bin, str(scripts / "content" / "build_document_registry.py"), "--config", "registry_config.json", "--output", "document_registry.md"], None, True),
        ("Link extraction", [python_bin, str(scripts / "content" / "link_extractor.py"), "docs/"], None, True),
        ("Push Confluence news", [python_bin, str(scripts / "publishing" / "push_confluence_news.py")], None, True),
        ("Push weekly update", [python_bin, str(scripts / "publishing" / "push_confluence_weekly.py")], None, True),
        ("Auto-commit", [python_bin, str(scripts / "automation" / "auto_commit_runner.py"), "--once"], None, True),
    ]


def get_hourly_steps(python_bin):
    """Return the quick hourly sync pipeline steps.

    Args:
        python_bin: Path to Python binary.

    Returns:
        list[tuple]: (name, command, env, allow_fail) tuples.
    """
    scripts = SCRIPT_DIR
    return [
        ("Google Drive sync", [python_bin, str(scripts / "sync" / "gdrive_sync.py")], None, True),
        ("Auto-commit", [python_bin, str(scripts / "automation" / "auto_commit_runner.py"), "--once"], None, True),
    ]


# ---------------------------------------------------------------------------
# Run state
# ---------------------------------------------------------------------------

def load_run_state():
    """Load the previous run state from disk.

    Returns:
        dict: Run state with last_run, results, etc.
    """
    if RUN_STATE_PATH.exists():
        return json.loads(RUN_STATE_PATH.read_text(encoding="utf-8"))
    return {"runs": []}


def save_run_state(state):
    """Save the current run state to disk.

    Args:
        state: Run state dict.
    """
    RUN_STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Archive log
# ---------------------------------------------------------------------------

def append_archive_log(mode, results):
    """Append a run summary to the archive log.

    Args:
        mode: Pipeline mode ('daily' or 'hourly').
        results: List of step result dicts.
    """
    log_path = os.environ.get("PAC_ARCHIVE_LOG")
    if not log_path:
        return

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    total_time = sum(r["duration"] for r in results)

    entry_lines = [
        f"\n### {mode.title()} Run - {now}",
        "",
        f"- Steps: {passed}/{total} passed, {failed} failed",
        f"- Duration: {total_time:.1f}s",
        "",
    ]

    if failed > 0:
        entry_lines.append("Failed steps:")
        for r in results:
            if not r["success"]:
                entry_lines.append(f"- {r['name']}: {r['error'][:100]}")
        entry_lines.append("")

    entry_lines.append("---")
    entry_lines.append("")

    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(entry_lines))


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_pipeline(mode):
    """Execute the pipeline for the given mode.

    Args:
        mode: 'daily' or 'hourly'.

    Returns:
        list[dict]: Step results.
    """
    python_bin = find_python()
    print(f"Python: {python_bin}")
    print(f"Mode: {mode}")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    if mode == "daily":
        steps = get_daily_steps(python_bin)
    else:
        steps = get_hourly_steps(python_bin)

    results = []
    for name, command, env, allow_fail in steps:
        result = run_step(name, command, env, allow_fail)
        results.append(result)

    # Summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"\n=== Pipeline complete: {passed}/{total} steps passed ===")

    # Save state
    state = load_run_state()
    state["runs"].append({
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "total": total,
        "results": results,
    })
    # Keep last 50 runs
    state["runs"] = state["runs"][-50:]
    save_run_state(state)

    # Archive log
    append_archive_log(mode, results)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Daily/hourly update runner for PAC pipelines"
    )
    parser.add_argument(
        "--mode",
        choices=["daily", "hourly"],
        default="daily",
        help="Pipeline mode: daily (full sync) or hourly (quick sync)",
    )
    args = parser.parse_args()

    results = run_pipeline(args.mode)

    # Exit with failure if any non-allow_fail step failed
    if any(not r["success"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
