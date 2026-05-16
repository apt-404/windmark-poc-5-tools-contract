import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

from shared.models import ToolResult

_ROOT = Path(__file__).resolve().parents[1]
_VARIANT_DIR = _ROOT / "variant-3-native-tooluse"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tools = _load_module("variant_3_native_tooluse_tools", _VARIANT_DIR / "tools.py")

NMAP_SCAN_SCHEMA = tools.NMAP_SCAN_SCHEMA
run_nmap = tools.run_nmap


def test_nmap_scan_schema_format():
    assert NMAP_SCAN_SCHEMA["type"] == "function"
    assert "parameters" in NMAP_SCAN_SCHEMA["function"]


def test_run_nmap_with_fixture():
    fixture_path = str(_ROOT / "traces" / "fixtures" / "nmap_scan.json")
    mock_completed = MagicMock(returncode=0, stdout="", stderr="")
    with patch("subprocess.run", return_value=mock_completed):
        result = run_nmap(fixture_path)

    assert isinstance(result, ToolResult)
    assert result.exit_code is not None


def test_run_nmap_missing_fixture_returns_error():
    result = run_nmap(str(_ROOT / "traces" / "fixtures" / "no_existe.json"))

    assert result.error is not None
    assert "fixture not found" in result.error
