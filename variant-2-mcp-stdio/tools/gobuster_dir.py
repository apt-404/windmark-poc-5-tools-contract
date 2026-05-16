import re
import subprocess
import time

TIMEOUT_SECONDS = 30
_FOUND_PATH_RE = re.compile(r"(/\S+)\s+\(Status:\s+(\d+)\)")


def gobuster_dir(target: str, wordlist: str, extensions: list[str] = None) -> dict:
    if extensions is None:
        extensions = []

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
        return {
            "raw_output": partial,
            "exit_code": -1,
            "error": "timeout",
            "duration_ms": duration_ms,
            "extra": {},
        }

    duration_ms = (time.perf_counter() - start) * 1000
    stdout = completed.stdout or ""

    found_paths: list[str] = []
    status_codes: dict[str, int] = {}
    for match in _FOUND_PATH_RE.finditer(stdout):
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

    return {
        "raw_output": stdout,
        "exit_code": completed.returncode,
        "error": error,
        "duration_ms": duration_ms,
        "extra": extra,
    }
