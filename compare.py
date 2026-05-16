import argparse
import glob
import json
import os
import queue
import shutil
import subprocess
import sys
import threading


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
    args = parser.parse_args()

    if args.check:
        sys.exit(run_check())

    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
