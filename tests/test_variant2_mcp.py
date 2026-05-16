import importlib.util
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_VARIANT_DIR = _ROOT / "variant-2-mcp-stdio"
_TOOLS_DIR = _VARIANT_DIR / "tools"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_line_with_timeout(proc: subprocess.Popen, timeout_s: float) -> bytes:
    response_queue: queue.Queue = queue.Queue()

    def _reader() -> None:
        try:
            line = proc.stdout.readline()
        except Exception:
            line = b""
        response_queue.put(line)

    reader_thread = threading.Thread(target=_reader, daemon=True)
    reader_thread.start()
    try:
        return response_queue.get(timeout=timeout_s)
    except queue.Empty:
        return b""


def _send(proc: subprocess.Popen, payload: dict) -> None:
    data = (json.dumps(payload) + "\n").encode("utf-8")
    proc.stdin.write(data)
    proc.stdin.flush()


def test_mcp_server_exposes_tools():
    server_path = _VARIANT_DIR / "server.py"
    proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    try:
        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1"},
                },
            },
        )
        init_line = _read_line_with_timeout(proc, timeout_s=3.0)
        assert init_line, "MCP server did not respond to initialize within 3s"

        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        _send(proc, {"jsonrpc": "2.0", "method": "tools/list", "id": 1})

        line = _read_line_with_timeout(proc, timeout_s=3.0)
        assert line, "MCP server did not respond to tools/list within 3s"

        response = json.loads(line.decode("utf-8"))
        tools = response.get("result", {}).get("tools", [])
        tool_names = {t.get("name") for t in tools}

        assert "nmap_scan" in tool_names
        assert "gobuster_dir" in tool_names
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)


def test_mcp_tools_modules_importable():
    nmap_module = _load_module(
        "variant_2_mcp_stdio_tools_nmap_scan",
        _TOOLS_DIR / "nmap_scan.py",
    )
    gobuster_module = _load_module(
        "variant_2_mcp_stdio_tools_gobuster_dir",
        _TOOLS_DIR / "gobuster_dir.py",
    )

    assert hasattr(nmap_module, "nmap_scan")
    assert hasattr(gobuster_module, "gobuster_dir")
