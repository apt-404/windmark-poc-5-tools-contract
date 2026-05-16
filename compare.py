import argparse
import glob
import os
import shutil
import subprocess
import sys


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
