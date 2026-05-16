# Aclaraciones sobre las variantes — PoC #5

> **Propósito de este documento.** Anexo didáctico que explica, con fragmentos de código reales del repositorio, qué implica concretamente cada variante y en qué se diferencian. Complementa los `requirements.md` y el `report.md`; no los reemplaza.

---

## Punto de partida: el contrato compartido

Las tres variantes comparten **el mismo contrato de entrada/salida**, definido en `shared/models.py`. Entenderlo es esencial antes de comparar nada.

```python
# shared/models.py
from pydantic import BaseModel, Field
from typing import Optional

class NmapScanInput(BaseModel):
    target: str
    ports: str = "1-1000"
    flags: list[str] = Field(default_factory=lambda: ["-sV"])

class GobusterDirInput(BaseModel):
    target: str
    wordlist: str
    extensions: list[str] = Field(default_factory=list)

class ToolResult(BaseModel):
    raw_output: str
    exit_code: int
    error: Optional[str] = None
    duration_ms: float
    extra: dict = Field(default_factory=dict)
```

`ToolResult` es el **sobre de respuesta invariante**: independientemente de cómo se invoque el tool (import directo, JSON-RPC o fixture), el runner siempre recibe un `ToolResult`. Esto permite comparar las tres variantes sobre el mismo contrato.

---

## Variante 1 — subprocess + Pydantic

### ¿Qué es?

El tool es una **función Python pura** tipada con los modelos de `shared/`. El runner la llama directamente por `import`. No hay proceso intermedio ni protocolo.

```
Runner ──import directo──► run(input: NmapScanInput) ──subprocess──► nmap
                                       │
                                       └─► ToolResult (en memoria)
```

### Código real

```python
# variant-1-subprocess/nmap_scan.py
from shared.models import NmapScanInput, ToolResult

TIMEOUT_SECONDS = 30
_OPEN_PORT_RE = re.compile(r"(\d+)/tcp\s+open\s+(\S+)")

def run(input: NmapScanInput) -> ToolResult:
    cmd = ["nmap"] + input.flags + ["-p", input.ports, input.target]
    start = time.perf_counter()
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        ...
        return ToolResult(raw_output=partial, exit_code=-1, error="timeout", ...)

    open_ports, service_fingerprints = [], {}
    for match in _OPEN_PORT_RE.finditer(completed.stdout):
        port = int(match.group(1))
        open_ports.append(port)
        service_fingerprints[str(port)] = match.group(2)

    return ToolResult(
        raw_output=completed.stdout,
        exit_code=completed.returncode,
        error=None if completed.returncode == 0 else (completed.stderr or "").strip(),
        duration_ms=(time.perf_counter() - start) * 1000,
        extra={"open_ports": open_ports, "service_fingerprints": service_fingerprints},
    )
```

### ¿Cómo expone el schema al LLM?

No lo expone directamente: el schema se **genera automáticamente** desde el modelo Pydantic.

```python
import json
from shared.models import NmapScanInput

schema = NmapScanInput.model_json_schema()
# → {"title": "NmapScanInput", "type": "object", "properties": {...}, "required": ["target"]}

token_footprint = len(json.dumps(schema)) // 4  # → 69 tokens estimados
```

Pydantic deriva el JSON Schema a partir de las anotaciones de tipo, incluyendo valores por defecto y campos requeridos. El resultado es el schema más compacto de las tres variantes.

### Lo que el runner hace en V1

```python
# compare.py (simplificado)
from variant_1_subprocess import nmap_scan as v1_nmap

result = v1_nmap.run(NmapScanInput(target="192.168.1.1", ports="22,80,443"))
# result es un ToolResult instanciado en el mismo proceso
```

---

## Variante 2 — MCP server stdio

### ¿Qué es?

El tool vive dentro de un **servidor FastMCP** que el runner arranca como subproceso. La comunicación es **JSON-RPC sobre stdin/stdout**. Hay un proceso separado; la llamada cruza una frontera de proceso.

```
Runner ──stdin (JSON-RPC)──► FastMCP server ──subprocess──► nmap
        ◄──stdout (JSON)────             │
                                         └─► ToolResult serializado a dict
```

### Código real — servidor

```python
# variant-2-mcp-stdio/server.py
from fastmcp import FastMCP
from tools.nmap_scan import nmap_scan as _nmap_scan

mcp = FastMCP("windmark-poc5-v2")

@mcp.tool()
def nmap_scan(target: str, ports: str = "1-1000", flags: list[str] = None) -> dict:
    return _nmap_scan(target=target, ports=ports, flags=flags)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

El decorador `@mcp.tool()` registra la función en el servidor **sin Pydantic**: FastMCP infiere el schema directamente de los type hints de Python (`str`, `list[str]`, etc.).

### Código real — tool interno

```python
# variant-2-mcp-stdio/tools/nmap_scan.py
def nmap_scan(target: str, ports: str = "1-1000", flags: list[str] = None) -> dict:
    if flags is None:
        flags = ["-sV"]
    cmd = ["nmap"] + flags + ["-p", ports, target]
    ...
    return {                        # ← dict, no ToolResult
        "raw_output": stdout,
        "exit_code": completed.returncode,
        "error": error,
        "duration_ms": duration_ms,
        "extra": extra,
    }
```

El tool devuelve un `dict` (no un `ToolResult`), porque el transporte MCP serializa la respuesta a JSON. El runner la deserializa en el otro extremo.

### ¿Cómo expone el schema al LLM?

El servidor responde al mensaje `tools/list` (JSON-RPC) con la descripción completa de las tools. FastMCP construye este schema a partir de los type hints y las docstrings.

```json
{
  "tools": [{
    "name": "nmap_scan",
    "description": "...",
    "inputSchema": {
      "type": "object",
      "properties": {
        "target": {"type": "string"},
        "ports": {"type": "string", "default": "1-1000"},
        "flags": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["target"]
    }
  }]
}
```

El schema que llega al LLM incluye el envoltorio del protocolo MCP, lo que aumenta el footprint: **118 tokens** estimados frente a los 69 de V1.

### Lo que el runner hace en V2

```python
# compare.py (simplificado)
import subprocess, json

proc = subprocess.Popen(["python", "variant-2-mcp-stdio/server.py"], stdin=PIPE, stdout=PIPE)

# 1. Esperar healthcheck: tools/list
proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "tools/list", "id": 1}) + "\n")
response = json.loads(proc.stdout.readline())

# 2. Invocar tool
proc.stdin.write(json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "nmap_scan", "arguments": {"target": "192.168.1.1"}},
    "id": 2
}) + "\n")
result_dict = json.loads(proc.stdout.readline())
# Convertir a ToolResult para la comparación
result = ToolResult(**result_dict)
```

---

## Variante 3 — Tool-use nativo del provider

### ¿Qué es?

V3 **simula el ciclo completo de tool-use del LLM** sin hacer llamadas reales a la API. El schema se define a mano en formato OpenAI `tools[]`. Los parámetros de invocación no vienen del runner sino de una **fixture pregrabada** que imita la respuesta del LLM.

```
Fixture JSON ──json.loads()──► params ──subprocess──► nmap
(respuesta LLM mockeada)              │
                                      └─► ToolResult
```

### Código real — schema a mano

```python
# variant-3-native-tooluse/tools.py

NMAP_SCAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "nmap_scan",
        "description": "Run an nmap scan against a target host or IP range...",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target host or IP range to scan."},
                "ports": {"type": "string", "description": "Port specification (e.g. '22,80,443')."},
                "flags": {"type": "array", "items": {"type": "string"}, "description": "..."},
            },
            "required": ["target"],
        },
    },
}
```

Esto es un `dict` Python escrito a mano en el formato que OpenAI (y compatible Anthropic) esperan en el parámetro `tools[]` de la API. **No se genera automáticamente**: el desarrollador lo mantiene manualmente.

### Código real — lectura de fixture y ejecución

```python
# variant-3-native-tooluse/tools.py

def run_nmap(fixture_path: str) -> ToolResult:
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)         # fixture = respuesta simulada del LLM
    except FileNotFoundError:
        return ToolResult(..., error=f"fixture not found: {fixture_path}")

    params = json.loads(data["function"]["arguments"])   # ← el LLM habría generado esto
    target = params["target"]
    ports = params.get("ports", "1-1000")
    flags = params.get("flags", ["-sV"])

    cmd = ["nmap"] + flags + ["-p", ports, target]
    # ... subprocess.run() igual que V1 ...
    return ToolResult(...)
```

La fixture tiene este aspecto (imita lo que el LLM devuelve en un `tool_use` block):

```json
{
  "function": {
    "name": "nmap_scan",
    "arguments": "{\"target\": \"192.168.1.1\", \"ports\": \"22,80,443\"}"
  }
}
```

Los argumentos están en `json.dumps()` dentro de un string, igual que en la respuesta real de la API de OpenAI/Anthropic.

### ¿Cómo expone el schema al LLM?

El schema `NMAP_SCAN_SCHEMA` se enviaría directamente al LLM en el campo `tools[]` de la llamada API. En esta PoC el LLM está mockeado, pero el schema está preparado para un uso real.

Token footprint: **131 tokens** estimados — el más alto, porque el envoltorio `type: function / function: {name, description, parameters}` es más verboso que el schema Pydantic de V1 o el esquema MCP de V2.

---

## Comparación directa

### Dónde vive el schema

| | V1 | V2 | V3 |
|---|---|---|---|
| **Origen del schema** | Generado por Pydantic desde la clase | Inferido por FastMCP desde los type hints | Escrito a mano como dict Python |
| **Formato** | JSON Schema (propiedad de Pydantic) | JSON Schema (protocolo MCP `tools/list`) | OpenAI `tools[]` |
| **Quién lo mantiene** | Solo la clase Pydantic | Solo los type hints de la función | El desarrollador, manualmente |
| **Token footprint** | **69** (más compacto) | 118 | 131 (más verboso) |

### Cómo viajan los parámetros al tool

| | V1 | V2 | V3 |
|---|---|---|---|
| **Origen de los params** | `NmapScanInput` construido por el runner | `arguments` JSON del mensaje `tools/call` | `function.arguments` de la fixture JSON |
| **Validación de params** | Pydantic (automática, en construcción) | FastMCP (type hints, sin Pydantic) | `json.loads()` manual, sin validación |
| **Frontera de proceso** | No (import directo) | Sí (stdin/stdout JSON-RPC) | No (import directo) |

### Cómo corre el binario

En las tres variantes el binario se ejecuta exactamente igual:

```python
subprocess.run(cmd, capture_output=True, text=True, timeout=30)
```

La diferencia está en **cómo llegan los parámetros** a ese `subprocess.run()`, no en cómo se ejecuta.

### Overhead de latencia

```
V1: runner → import → subprocess.run()
V2: runner → JSON-RPC (stdin) → server → subprocess.run() → JSON-RPC (stdout) → runner
V3: runner → open(fixture) → json.loads() → subprocess.run()
```

- **V1** es el camino más corto: llamada en proceso, sin serialización.
- **V2** paga el overhead de JSON-RPC sobre stdio más el startup del proceso FastMCP.
- **V3** es comparable a V1 en latencia de ejecución (misma ruta de subprocess), pero el LLM real añadiría latencia de inferencia que esta PoC no mide.

### Aislamiento entre variantes

Las tres variantes están completamente aisladas: **ninguna importa código de las otras**. El parser de nmap con regex está reimplementado en los tres módulos de forma independiente. Esto es una decisión explícita del diseño para medir cada variante sin contaminación de dependencias.

---

## Resumen visual de la arquitectura de cada variante

```
┌─────────────────────────────────────────────────────────────────┐
│                         compare.py (runner)                     │
│                                                                 │
│  V1: import v1_nmap ──────────────────────────────────────────► │
│      run(NmapScanInput(...))  ←──── ToolResult ───────────────  │
│                                                                 │
│  V2: Popen(server.py) ─── stdin (JSON-RPC) ──► FastMCP server  │
│      ◄──── stdout (JSON) ──── dict ◄──────────────────────────  │
│      ToolResult(**dict)                                         │
│                                                                 │
│  V3: import v3_tools ─────────────────────────────────────────► │
│      run_nmap("traces/fixtures/nmap_htb.json")                  │
│                          ↑ lee params del "LLM simulado"        │
│      ←──── ToolResult ─────────────────────────────────────────  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cuándo elegirías cada variante en producción

| Situación | Variante recomendada | Motivo |
|---|---|---|
| Tool embebido en el mismo proceso Python que el agente | **V1** | Mínima latencia, máxima simplicidad, schema más compacto |
| Tool que debe ser accesible desde múltiples agentes o lenguajes diferentes | **V2** | MCP como protocolo de interoperabilidad estándar |
| Integración directa con la API del provider (OpenAI, Anthropic) sin infraestructura adicional | **V3** | El schema `tools[]` se envía directamente en la llamada API |
| Schema compartido con validación estricta de tipos | **V1** | Pydantic garantiza que los parámetros son correctos antes de llegar al subprocess |

La PoC concluye que **V1 es la mejor opción para este caso de uso**: menor token footprint, latencia comparable a V3, y sin dependencia de protocolo externo ni de fixtures mockeadas.
