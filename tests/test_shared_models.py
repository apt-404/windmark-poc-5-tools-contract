from shared.models import NmapScanInput, GobusterDirInput, ToolResult


def test_nmap_schema_fields():
    schema = NmapScanInput.model_json_schema()
    properties = schema["properties"]
    assert "target" in properties
    assert "ports" in properties
    assert "flags" in properties


def test_gobuster_schema_fields():
    schema = GobusterDirInput.model_json_schema()
    properties = schema["properties"]
    assert "target" in properties
    assert "wordlist" in properties


def test_tool_result_defaults():
    result = ToolResult(raw_output="x", exit_code=0, duration_ms=1.0)
    assert result.error is None
    assert result.extra == {}
