import argparse
import glob
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone


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

    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
