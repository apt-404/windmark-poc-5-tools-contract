import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from shared.models import GobusterDirInput, NmapScanInput, ToolResult

_ROOT = Path(__file__).resolve().parents[1]
_VARIANT_DIR = _ROOT / "variant-1-subprocess"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


nmap_scan = _load_module("nmap_scan", _VARIANT_DIR / "nmap_scan.py")
gobuster_dir = _load_module("gobuster_dir", _VARIANT_DIR / "gobuster_dir.py")

run_nmap = nmap_scan.run
run_gobuster = gobuster_dir.run


def test_run_nmap_returns_tool_result():
    mock_completed = MagicMock(returncode=0, stdout="", stderr="")
    with patch("subprocess.run", return_value=mock_completed):
        result = run_nmap(NmapScanInput(target="127.0.0.1"))

    assert isinstance(result, ToolResult)
    assert result.exit_code is not None
    assert isinstance(result.extra, dict)


def test_run_gobuster_returns_tool_result():
    mock_completed = MagicMock(returncode=0, stdout="", stderr="")
    with patch("subprocess.run", return_value=mock_completed):
        result = run_gobuster(
            GobusterDirInput(target="http://127.0.0.1", wordlist="/tmp/words.txt")
        )

    assert isinstance(result, ToolResult)
    assert result.exit_code is not None
    assert isinstance(result.extra, dict)


def test_run_nmap_timeout_sets_error():
    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["nmap"], timeout=30)

    with patch("subprocess.run", side_effect=_raise_timeout):
        result = run_nmap(NmapScanInput(target="127.0.0.1"))

    assert result.error == "timeout"
