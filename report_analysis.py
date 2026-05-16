import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_V2_DIR = _ROOT / "variant-2-mcp-stdio"
_V3_DIR = _ROOT / "variant-3-native-tooluse"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _token_footprint(schema: dict) -> int:
    return len(json.dumps(schema)) // 4


def compute_duration_means(records: list[dict]) -> tuple[dict, int]:
    sums: dict[tuple[str, str], list[float]] = {}
    excluded = 0
    for r in records:
        variant = r.get("variant")
        tool = r.get("tool")
        if r.get("error") is not None:
            excluded += 1
            continue
        sums.setdefault((variant, tool), []).append(float(r.get("duration_ms", 0.0)))
    means: dict = {}
    for (variant, tool), values in sums.items():
        means.setdefault(variant, {})[tool] = sum(values) / len(values)
    return means, excluded


def compute_success_rate(records: list[dict]) -> dict:
    totals: dict[str, dict[str, int]] = {}
    for r in records:
        variant = r.get("variant")
        entry = totals.setdefault(variant, {"ok": 0, "total": 0})
        entry["total"] += 1
        if r.get("error") is None:
            entry["ok"] += 1
    return {
        v: {
            "ok": e["ok"],
            "total": e["total"],
            "rate": (e["ok"] / e["total"]) if e["total"] else 0.0,
        }
        for v, e in totals.items()
    }


def _v1_nmap_schema() -> dict:
    from shared.models import NmapScanInput

    return NmapScanInput.model_json_schema()


def _v2_nmap_schema() -> dict:
    sys.path.insert(0, str(_V2_DIR))
    try:
        server = _load_module("v2_server", _V2_DIR / "server.py")
        tools = asyncio.run(server.mcp.list_tools())
    finally:
        if str(_V2_DIR) in sys.path:
            sys.path.remove(str(_V2_DIR))
    for tool in tools:
        if tool.name == "nmap_scan":
            return tool.to_mcp_tool().model_dump()
    raise RuntimeError("nmap_scan tool not found in v2 FastMCP server")


def _v3_nmap_schema() -> dict:
    tools = _load_module("v3_tools", _V3_DIR / "tools.py")
    return tools.NMAP_SCAN_SCHEMA


def compute_token_footprint() -> dict:
    return {
        "v1": _token_footprint(_v1_nmap_schema()),
        "v2": _token_footprint(_v2_nmap_schema()),
        "v3": _token_footprint(_v3_nmap_schema()),
    }


def analyze(metrics_path: Path) -> dict:
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    records = payload.get("results", [])
    duration_means, excluded = compute_duration_means(records)
    success_rate = compute_success_rate(records)
    token_footprint = compute_token_footprint()
    return {
        "metrics_source": str(metrics_path),
        "total_invocations": len(records),
        "duration_ms_mean": duration_means,
        "excluded_from_duration_mean": excluded,
        "success_rate": success_rate,
        "token_footprint_schema": token_footprint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analiza traces/metrics.json e imprime el dict de resultados como JSON."
    )
    parser.add_argument(
        "--metrics",
        type=str,
        default="traces/metrics.json",
        help="Ruta a metrics.json (por defecto traces/metrics.json).",
    )
    args = parser.parse_args()

    metrics_path = Path(args.metrics)
    if not metrics_path.is_file():
        print(
            f"metrics.json no encontrado en {metrics_path}; "
            "F1.8 debe generar el run real antes de ejecutar el análisis.",
            file=sys.stderr,
        )
        return 1

    result = analyze(metrics_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
