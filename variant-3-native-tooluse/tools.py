import json
import re
import subprocess
import time

from shared.models import ToolResult

TIMEOUT_SECONDS = 30
_OPEN_PORT_RE = re.compile(r"(\d+)/tcp\s+open\s+(\S+)")
_GOBUSTER_PATH_RE = re.compile(r"^(/\S+)\s+\(Status:\s*(\d+)\)", re.MULTILINE)


NMAP_SCAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "nmap_scan",
        "description": "Run an nmap scan against a target host or IP range and return open ports and service fingerprints.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Target host or IP range to scan.",
                },
                "ports": {
                    "type": "string",
                    "description": "Port specification (e.g. '22,80,443' or '1-1000').",
                },
                "flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional nmap CLI flags.",
                },
            },
            "required": ["target"],
        },
    },
}


GOBUSTER_DIR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "gobuster_dir",
        "description": "Run gobuster in dir mode against a target URL to discover directories and files using a wordlist.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Target URL to brute-force (e.g. 'http://example.com').",
                },
                "wordlist": {
                    "type": "string",
                    "description": "Path to the wordlist file.",
                },
                "extensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File extensions to append to each word (e.g. ['php', 'html']).",
                },
            },
            "required": ["target", "wordlist"],
        },
    },
}


def run_nmap(fixture_path: str) -> ToolResult:
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return ToolResult(
            raw_output="",
            exit_code=-1,
            error=f"fixture not found: {fixture_path}",
            duration_ms=0.0,
            extra={},
        )

    params = json.loads(data["function"]["arguments"])
    target = params["target"]
    ports = params.get("ports", "1-1000")
    flags = params.get("flags", ["-sV"])

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
        return ToolResult(
            raw_output=partial,
            exit_code=-1,
            error="timeout",
            duration_ms=duration_ms,
            extra={},
        )

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

    return ToolResult(
        raw_output=stdout,
        exit_code=completed.returncode,
        error=error,
        duration_ms=duration_ms,
        extra=extra,
    )


def run_gobuster(fixture_path: str) -> ToolResult:
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return ToolResult(
            raw_output="",
            exit_code=-1,
            error=f"fixture not found: {fixture_path}",
            duration_ms=0.0,
            extra={},
        )

    params = json.loads(data["function"]["arguments"])
    target = params["target"]
    wordlist = params["wordlist"]
    extensions = params.get("extensions", [])

    cmd = ["gobuster", "dir", "-u", target, "-w", wordlist]
    if extensions:
        cmd += ["-x", ",".join(extensions)]

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
        return ToolResult(
            raw_output=partial,
            exit_code=-1,
            error="timeout",
            duration_ms=duration_ms,
            extra={},
        )

    duration_ms = (time.perf_counter() - start) * 1000
    stdout = completed.stdout or ""

    found_paths: list[str] = []
    status_codes: dict[str, int] = {}
    for match in _GOBUSTER_PATH_RE.finditer(stdout):
        path = match.group(1)
        status = int(match.group(2))
        found_paths.append(path)
        status_codes[path] = status

    extra = {
        "found_paths": found_paths,
        "status_codes": status_codes,
    }

    error = None
    if completed.returncode != 0:
        error = (completed.stderr or "").strip() or f"exit_code={completed.returncode}"

    return ToolResult(
        raw_output=stdout,
        exit_code=completed.returncode,
        error=error,
        duration_ms=duration_ms,
        extra=extra,
    )
