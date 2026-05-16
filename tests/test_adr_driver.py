from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRIVER_PATH = ROOT / "outputs" / "driver.md"


def test_driver_contains_required_sections():
    assert DRIVER_PATH.is_file(), f"outputs/driver.md no existe en {DRIVER_PATH}"
    content = DRIVER_PATH.read_text(encoding="utf-8")

    assert "## Contrato elegido" in content
    assert "## Evidencia" in content
    assert "## Triggers de upgrade a MCP" in content
    assert "## Riesgos asumidos" in content


def test_driver_references_evidence_source():
    assert DRIVER_PATH.is_file(), f"outputs/driver.md no existe en {DRIVER_PATH}"
    content = DRIVER_PATH.read_text(encoding="utf-8")

    assert "report.md" in content or "metrics.json" in content, (
        "outputs/driver.md no contiene referencia a report.md o metrics.json como fuente de evidencia"
    )
