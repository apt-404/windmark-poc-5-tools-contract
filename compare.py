import argparse
import glob
import importlib.util
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from shared.models import GobusterDirInput, NmapScanInput, ToolResult

_ROOT = Path(__file__).resolve().parent
_V1_DIR = _ROOT / "variant-1-subprocess"
_V3_DIR = _ROOT / "variant-3-native-tooluse"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check_binary(name: str) -> tuple[str, bool]:
    return name, shutil.which(name) is not None


def _check_wordlist() -> tuple[str, bool]:
    path = os.environ.get("WORDLIST_PATH", "/usr/share/wordlists/dirb/common.txt")
    return f"wordlist ({path})", os.path.isfile(path)


def _check_fixtures() -> tuple[str, bool]:
    fixtures = glob.glob("traces/fixtures/*.json")
    return "fixtures (traces/fixtures/*.json)", len(fixtures) > 0


def _check_target_ip() -> tuple[str, bool] | None:
    target_ip = os.environ.get("TARGET_IP")
    if not target_ip:
        return None
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", target_ip],
            capture_output=True,
        )
        return f"ping {target_ip}", result.returncode == 0
    except FileNotFoundError:
        return f"ping {target_ip}", False


def _print_table(rows: list[tuple[str, bool]]) -> None:
    header_dep = "Dependencia"
    header_estado = "Estado"
    dep_width = max(len(header_dep), max(len(r[0]) for r in rows))
    estado_width = max(len(header_estado), len("ERROR"))
    sep = f"+{'-' * (dep_width + 2)}+{'-' * (estado_width + 2)}+"
    print(sep)
    print(f"| {header_dep:<{dep_width}} | {header_estado:<{estado_width}} |")
    print(sep)
    for name, ok in rows:
        estado = "OK" if ok else "ERROR"
        print(f"| {name:<{dep_width}} | {estado:<{estado_width}} |")
    print(sep)


def start_mcp_server() -> subprocess.Popen:
    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "variant-2-mcp-stdio",
        "server.py",
    )
    return subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )


def wait_for_mcp_ready(proc: subprocess.Popen, timeout_s: float) -> bool:
    message = json.dumps({"jsonrpc": "2.0", "method": "tools/list", "id": 1}) + "\n"
    try:
        proc.stdin.write(message.encode("utf-8"))
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
        return False

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
        line = response_queue.get(timeout=timeout_s)
    except queue.Empty:
        return False
    return bool(line)


def write_jsonl(result, variant: str, tool: str, output_dir: str) -> str:
    dir_path = os.path.join(output_dir, variant, tool)
    os.makedirs(dir_path, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    file_path = os.path.join(dir_path, f"{timestamp}.jsonl")
    raw_output = getattr(result, "raw_output", "") or ""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "variant": variant,
        "tool": tool,
        "duration_ms": getattr(result, "duration_ms", 0.0),
        "exit_code": getattr(result, "exit_code", -1),
        "error": getattr(result, "error", None),
        "output_summary": raw_output[:200],
    }
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return file_path


def consolidate_metrics(results: list, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "metrics.json")
    serialized = []
    for entry in results:
        if isinstance(entry, dict):
            serialized.append(entry)
            continue
        raw_output = getattr(entry, "raw_output", "") or ""
        serialized.append(
            {
                "variant": getattr(entry, "variant", None),
                "tool": getattr(entry, "tool", None),
                "duration_ms": getattr(entry, "duration_ms", 0.0),
                "exit_code": getattr(entry, "exit_code", -1),
                "error": getattr(entry, "error", None),
                "output_summary": raw_output[:200],
            }
        )
    variants_ok = sum(1 for r in serialized if r.get("error") is None)
    variants_error = sum(1 for r in serialized if r.get("error") is not None)
    payload = {
        "total_invocations": len(serialized),
        "variants_ok": variants_ok,
        "variants_error": variants_error,
        "results": serialized,
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return file_path


def run_v1(target: str, tool: str, output_dir: str) -> ToolResult:
    start = time.perf_counter()
    try:
        if tool == "nmap_scan":
            module = _load_module("v1_nmap_scan", _V1_DIR / "nmap_scan.py")
            result = module.run(NmapScanInput(target=target))
        elif tool == "gobuster_dir":
            wordlist = os.environ.get(
                "WORDLIST_PATH", "/usr/share/wordlists/dirb/common.txt"
            )
            module = _load_module("v1_gobuster_dir", _V1_DIR / "gobuster_dir.py")
            result = module.run(GobusterDirInput(target=target, wordlist=wordlist))
        else:
            raise ValueError(f"unknown tool: {tool}")
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return ToolResult(
            raw_output="",
            exit_code=-1,
            error=f"v1_error: {exc}",
            duration_ms=duration_ms,
            extra={},
        )
    result.duration_ms = (time.perf_counter() - start) * 1000
    return result


def _read_mcp_line(proc: subprocess.Popen, timeout_s: float) -> bytes:
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


def _send_mcp(proc: subprocess.Popen, payload: dict) -> None:
    data = (json.dumps(payload) + "\n").encode("utf-8")
    proc.stdin.write(data)
    proc.stdin.flush()


def run_v2(
    target: str,
    tool: str,
    output_dir: str,
    timeout_s: float = 10.0,
) -> ToolResult:
    start = time.perf_counter()
    proc = None
    try:
        proc = start_mcp_server()
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return ToolResult(
            raw_output="",
            exit_code=-1,
            error=f"v2_error: {exc}",
            duration_ms=duration_ms,
            extra={},
        )

    try:
        if not wait_for_mcp_ready(proc, timeout_s):
            duration_ms = (time.perf_counter() - start) * 1000
            return ToolResult(
                raw_output="",
                exit_code=-1,
                error="mcp_server_timeout",
                duration_ms=duration_ms,
                extra={},
            )

        try:
            _send_mcp(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 100,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "compare-runner", "version": "1"},
                    },
                },
            )
            init_line = _read_mcp_line(proc, timeout_s)
            if not init_line:
                duration_ms = (time.perf_counter() - start) * 1000
                return ToolResult(
                    raw_output="",
                    exit_code=-1,
                    error="mcp_server_timeout",
                    duration_ms=duration_ms,
                    extra={},
                )
            _send_mcp(
                proc,
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
            )

            if tool == "nmap_scan":
                arguments = {"target": target, "ports": "1-1000", "flags": ["-sV"]}
            elif tool == "gobuster_dir":
                wordlist = os.environ.get(
                    "WORDLIST_PATH", "/usr/share/wordlists/dirb/common.txt"
                )
                arguments = {
                    "target": target,
                    "wordlist": wordlist,
                    "extensions": [],
                }
            else:
                raise ValueError(f"unknown tool: {tool}")

            _send_mcp(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 101,
                    "method": "tools/call",
                    "params": {"name": tool, "arguments": arguments},
                },
            )

            call_line = _read_mcp_line(proc, timeout_s)
            if not call_line:
                duration_ms = (time.perf_counter() - start) * 1000
                return ToolResult(
                    raw_output="",
                    exit_code=-1,
                    error="v2_no_response",
                    duration_ms=duration_ms,
                    extra={},
                )

            response = json.loads(call_line.decode("utf-8"))
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            return ToolResult(
                raw_output="",
                exit_code=-1,
                error=f"v2_error: {exc}",
                duration_ms=duration_ms,
                extra={},
            )

        duration_ms = (time.perf_counter() - start) * 1000

        if "error" in response:
            return ToolResult(
                raw_output="",
                exit_code=-1,
                error=f"v2_error: {response['error']}",
                duration_ms=duration_ms,
                extra={},
            )

        result_data = response.get("result", {}) or {}
        structured = result_data.get("structuredContent") or {}
        content = result_data.get("content") or []
        is_error = bool(result_data.get("isError", False))

        raw_output = ""
        exit_code = 0 if not is_error else -1
        error = None
        extra: dict = {}

        if isinstance(structured, dict) and structured:
            raw_output = structured.get("raw_output", "") or ""
            exit_code = structured.get("exit_code", exit_code)
            error = structured.get("error")
            extra = structured.get("extra", {}) or {}
        elif content:
            texts = [
                c.get("text", "")
                for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            ]
            raw_output = "\n".join(texts)

        return ToolResult(
            raw_output=raw_output,
            exit_code=exit_code,
            error=error,
            duration_ms=duration_ms,
            extra=extra,
        )
    finally:
        if proc is not None:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            except Exception:
                pass


def run_v3(target: str, tool: str, fixture_dir: str, output_dir: str) -> ToolResult:
    start = time.perf_counter()
    try:
        module = _load_module("v3_tools", _V3_DIR / "tools.py")
        fixture_path = os.path.join(fixture_dir, f"{tool}.json")
        if tool == "nmap_scan":
            result = module.run_nmap(fixture_path)
        elif tool == "gobuster_dir":
            result = module.run_gobuster(fixture_path)
        else:
            raise ValueError(f"unknown tool: {tool}")
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return ToolResult(
            raw_output="",
            exit_code=-1,
            error=f"v3_error: {exc}",
            duration_ms=duration_ms,
            extra={},
        )
    return result


def run_check() -> int:
    rows: list[tuple[str, bool]] = []
    rows.append(_check_binary("nmap"))
    rows.append(_check_binary("gobuster"))
    rows.append(_check_wordlist())
    rows.append(_check_fixtures())
    ping_result = _check_target_ip()
    if ping_result is not None:
        rows.append(ping_result)

    _print_table(rows)

    all_ok = all(ok for _, ok in rows)
    return 0 if all_ok else 1


def _result_to_record(result: ToolResult, variant: str, tool: str) -> dict:
    raw_output = getattr(result, "raw_output", "") or ""
    return {
        "variant": variant,
        "tool": tool,
        "duration_ms": getattr(result, "duration_ms", 0.0),
        "exit_code": getattr(result, "exit_code", -1),
        "error": getattr(result, "error", None),
        "output_summary": raw_output[:200],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="compare runner / healthcheck")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verifica dependencias del entorno y sale con código 0/1.",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target sobre el que invocar las variantes.",
    )
    parser.add_argument(
        "--variant",
        type=str,
        default="all",
        choices=["v1", "v2", "v3", "all"],
        help="Variante a ejecutar: v1, v2, v3 o all.",
    )
    parser.add_argument(
        "--tool",
        type=str,
        default="all",
        choices=["nmap_scan", "gobuster_dir", "all"],
        help="Tool a invocar: nmap_scan, gobuster_dir o all.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="traces/",
        help="Directorio de salida para JSONL y metrics.json.",
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(run_check())

    if not args.target:
        parser.error("--target es obligatorio cuando no se usa --check")

    variants = ["v1", "v2", "v3"] if args.variant == "all" else [args.variant]
    tools = ["nmap_scan", "gobuster_dir"] if args.tool == "all" else [args.tool]
    fixture_dir = os.path.join(args.output, "fixtures")

    results: list[dict] = []

    for tool in tools:
        for variant in variants:
            try:
                if variant == "v1":
                    result = run_v1(args.target, tool, args.output)
                elif variant == "v2":
                    result = run_v2(args.target, tool, args.output)
                elif variant == "v3":
                    result = run_v3(args.target, tool, fixture_dir, args.output)
                else:
                    result = ToolResult(
                        raw_output="",
                        exit_code=-1,
                        error=f"unknown_variant: {variant}",
                        duration_ms=0.0,
                        extra={},
                    )
            except Exception as exc:
                result = ToolResult(
                    raw_output="",
                    exit_code=-1,
                    error=f"unexpected_error: {exc}",
                    duration_ms=0.0,
                    extra={},
                )

            try:
                write_jsonl(result, variant, tool, args.output)
            except Exception as exc:
                print(
                    f"warning: no se pudo escribir JSONL para {variant}/{tool}: {exc}",
                    file=sys.stderr,
                )

            results.append(_result_to_record(result, variant, tool))

    consolidate_metrics(results, args.output)

    any_ok = any(r.get("error") is None for r in results)
    sys.exit(0 if any_ok else 1)


if __name__ == "__main__":
    main()
