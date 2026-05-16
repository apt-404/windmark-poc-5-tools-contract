import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "outputs" / "report.md"
METRICS_PATH = ROOT / "traces" / "metrics.json"


def test_report_contains_required_sections():
    assert REPORT_PATH.is_file(), f"outputs/report.md no existe en {REPORT_PATH}"
    content = REPORT_PATH.read_text(encoding="utf-8")

    assert "## Hipótesis evaluadas" in content
    assert "## Métricas comparativas" in content
    assert "## Limitaciones" in content


def test_report_references_all_variants():
    if not METRICS_PATH.is_file():
        pytest.skip(
            f"traces/metrics.json no existe (requiere F1.8); no se pueden extraer variantes"
        )

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)

    results = payload.get("results", [])
    variants = {r["variant"] for r in results if "variant" in r}
    assert variants, "metrics.json no contiene variantes en results[]"

    assert REPORT_PATH.is_file(), f"outputs/report.md no existe en {REPORT_PATH}"
    report_text = REPORT_PATH.read_text(encoding="utf-8")

    for variant in variants:
        assert variant in report_text, (
            f"La variante '{variant}' de metrics.json no aparece en outputs/report.md"
        )
