import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compare import consolidate_metrics, write_jsonl  # noqa: E402
from shared.models import ToolResult  # noqa: E402


def test_write_jsonl_creates_file_with_fields(tmp_path):
    result = ToolResult(
        raw_output="sample nmap output",
        exit_code=0,
        error=None,
        duration_ms=123.45,
        extra={},
    )

    file_path = write_jsonl(result, "v1", "nmap_scan", str(tmp_path))

    assert os.path.isfile(file_path)
    expected_dir = tmp_path / "v1" / "nmap_scan"
    assert Path(file_path).parent == expected_dir

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line for line in f.read().splitlines() if line.strip()]

    assert len(lines) >= 1
    record = json.loads(lines[0])
    assert "exit_code" in record
    assert "duration_ms" in record
    assert "variant" in record
    assert record["variant"] == "v1"
    assert record["exit_code"] == 0
    assert record["duration_ms"] == 123.45


def test_consolidate_metrics_structure(tmp_path):
    results_list = [
        {
            "variant": "v1",
            "tool": "nmap_scan",
            "duration_ms": 100.0,
            "exit_code": 0,
            "error": None,
            "output_summary": "ok",
        },
        {
            "variant": "v2",
            "tool": "nmap_scan",
            "duration_ms": 200.0,
            "exit_code": 0,
            "error": None,
            "output_summary": "ok",
        },
        {
            "variant": "v3",
            "tool": "gobuster_dir",
            "duration_ms": 150.0,
            "exit_code": -1,
            "error": "v3_error: boom",
            "output_summary": "",
        },
    ]

    file_path = consolidate_metrics(results_list, str(tmp_path))

    assert os.path.isfile(file_path)
    assert Path(file_path).name == "metrics.json"

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    assert "total_invocations" in payload
    assert "results" in payload
    assert "variants_ok" in payload
    assert payload["total_invocations"] == 3
    assert payload["variants_ok"] == 2
    assert isinstance(payload["results"], list)
    assert len(payload["results"]) == 3


def test_variant_error_captured_in_metrics(tmp_path):
    timeout_result = ToolResult(
        raw_output="",
        exit_code=-1,
        error="mcp_server_timeout",
        duration_ms=10000.0,
        extra={},
    )
    results_list = [
        {
            "variant": "v2",
            "tool": "nmap_scan",
            "duration_ms": timeout_result.duration_ms,
            "exit_code": timeout_result.exit_code,
            "error": timeout_result.error,
            "output_summary": "",
        },
    ]

    file_path = consolidate_metrics(results_list, str(tmp_path))

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    errors = [r.get("error") for r in payload["results"]]
    assert "mcp_server_timeout" in errors
    assert payload["variants_error"] >= 1
    assert payload["variants_ok"] == 0
