import re
import subprocess
import time

TIMEOUT_SECONDS = 30
_OPEN_PORT_RE = re.compile(r"(\d+)/tcp\s+open\s+(\S+)")


def nmap_scan(target: str, ports: str = "1-1000", flags: list[str] = None) -> dict:
    if flags is None:
        flags = ["-sV"]

    cmd = ["nmap"] + flags + ["-p", ports, target]
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return {
            "raw_output": partial,
            "exit_code": -1,
            "error": "timeout",
            "duration_ms": duration_ms,
            "extra": {},
        }

    duration_ms = (time.perf_counter() - start) * 1000
    stdout = completed.stdout or ""

    open_ports: list[int] = []
    service_fingerprints: dict[str, str] = {}
    for match in _OPEN_PORT_RE.finditer(stdout):
        port = int(match.group(1))
        service = match.group(2)
        open_ports.append(port)
        service_fingerprints[str(port)] = service

    extra = {
        "open_ports": open_ports,
        "service_fingerprints": service_fingerprints,
    }

    error = None
    if completed.returncode != 0:
        error = (completed.stderr or "").strip() or f"exit_code={completed.returncode}"

    return {
        "raw_output": stdout,
        "exit_code": completed.returncode,
        "error": error,
        "duration_ms": duration_ms,
        "extra": extra,
    }
