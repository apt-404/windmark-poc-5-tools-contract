import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import compare  # noqa: E402
from compare import consolidate_metrics, main  # noqa: E402
from shared.models import ToolResult  # noqa: E402


def test_repeat_argument_iterates_n_times(tmp_path):
    fake_result = ToolResult(
        raw_output="fake",
        exit_code=0,
        error=None,
        duration_ms=10.0,
        extra={},
    )

    argv = [
        "compare.py",
        "--repeat",
        "2",
        "--variant",
        "v1",
        "--tool",
        "nmap_scan",
        "--target",
        "127.0.0.1",
        "--output",
        str(tmp_path),
    ]

    with patch.object(compare, "run_v1", return_value=fake_result) as mock_run_v1:
        with patch.object(sys, "argv", argv):
            with pytest.raises(SystemExit):
                main()

    assert mock_run_v1.call_count == 2


def test_metrics_contains_mean_when_repeat_gt_1(tmp_path):
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
            "variant": "v1",
            "tool": "nmap_scan",
            "duration_ms": 200.0,
            "exit_code": 0,
            "error": None,
            "output_summary": "ok",
        },
    ]

    file_path = consolidate_metrics(results_list, str(tmp_path), repeat=2)

    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    assert "summary" in payload
    assert any("duration_ms_mean" in entry for entry in payload["summary"])
