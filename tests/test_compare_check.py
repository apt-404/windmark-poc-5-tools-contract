import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run_check(extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "TARGET_IP"}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "compare.py", "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )


def test_check_output_contains_dependency_table():
    result = _run_check()
    stdout = result.stdout
    assert "nmap" in stdout
    assert "gobuster" in stdout
    assert "wordlist" in stdout


def test_check_returncode_without_fixtures():
    fixtures_dir = ROOT / "traces" / "fixtures"
    assert not fixtures_dir.exists() or not any(fixtures_dir.glob("*.json"))

    result = _run_check()
    assert result.returncode == 1
