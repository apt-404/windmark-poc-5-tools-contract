import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = ROOT / "traces" / "fixtures"


def test_nmap_fixture_structure():
    fixture_path = FIXTURES_DIR / "nmap_scan.json"
    with fixture_path.open(encoding="utf-8") as f:
        fixture = json.load(f)

    arguments = json.loads(fixture["function"]["arguments"])
    assert arguments["target"] == "192.168.1.1"
    assert arguments["ports"] == "1-1000"
    assert arguments["flags"] == ["-sV"]


def test_gobuster_fixture_structure():
    fixture_path = FIXTURES_DIR / "gobuster_dir.json"
    with fixture_path.open(encoding="utf-8") as f:
        fixture = json.load(f)

    arguments = json.loads(fixture["function"]["arguments"])
    assert "target" in arguments
    assert "wordlist" in arguments
    assert "extensions" in arguments
