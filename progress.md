# Progress — windmark-poc-5-tools-contract

## Estado global

| Total | Completadas | En progreso | Bloqueadas | Pendientes |
|-------|-------------|-------------|------------|------------|
| 41    | 0           | 0           | 0          | 41         |

## F1.1 — F1.1 Contrato de datos compartido

### Implementación del paquete shared

- [ ] f1.1-01: Crear el directorio `shared/` con `shared/__init__.py` vacío y `shared/models.py` con los imports base.
- [ ] f1.1-02: Implementar en `shared/models.py` las tres clases Pydantic: `NmapScanInput`, `GobusterDirInput` y `ToolResult`.

### Verificación

- [ ] f1.1-03: Ejecutar verificación de imports y schemas de los tres modelos Pydantic.

## F1.2 — F1.2 Entorno Docker + healthcheck

### Configuración de dependencias

- [ ] f1.2-01: Crear `pyproject.toml` y ejecutar `uv lock` para generar `uv.lock`.

### Dockerfile

- [ ] f1.2-02: Crear `Dockerfile` completo con instalación de nmap, gobuster y uv.

### Subcomando --check en compare.py

- [ ] f1.2-03: Crear `compare.py` con subcomando `--check` que verifica binarios, wordlist y fixtures.

### Verificación

- [ ] f1.2-04: Ejecutar `docker build` y confirmar que nmap y gobuster responden dentro del contenedor.
- [ ] f1.2-05: Ejecutar `python compare.py --check` sin `TARGET_IP` y confirmar código de salida 1 con líneas esperadas en stdout.

## F1.3 — F1.3 Fixtures LLM pregrabadas

### Creación de fixtures

- [ ] f1.3-01: Crear `traces/fixtures/nmap_scan.json` y `traces/fixtures/gobuster_dir.json` con estructura OpenAI function_call.

### Verificación

- [ ] f1.3-02: Verificar estructura y campos de ambas fixtures con python -c.
- [ ] f1.3-03: Ejecutar `python compare.py --check` y confirmar estado OK para fixtures.

## F1.4 — F1.4 Variante 1: subprocess + Pydantic

### Módulo nmap_scan

- [ ] f1.4-01: Crear `variant-1-subprocess/nmap_scan.py` con función `run(input: NmapScanInput) -> ToolResult`.

### Módulo gobuster_dir

- [ ] f1.4-02: Crear `variant-1-subprocess/gobuster_dir.py` con función `run(input: GobusterDirInput) -> ToolResult`.

### Verificación

- [ ] f1.4-03: Verificar desde Docker que ambos módulos ejecutan y retornan ToolResult válido.

## F1.5 — F1.5 Variante 2: MCP server stdio

### Tools MCP

- [ ] f1.5-01: Crear directorio `variant-2-mcp-stdio/` con tools `nmap_scan.py` y `gobuster_dir.py`.

### Servidor FastMCP

- [ ] f1.5-02: Crear `variant-2-mcp-stdio/server.py` con FastMCP y transporte stdio.

### Integración en compare.py

- [ ] f1.5-03: Añadir `start_mcp_server()` y `wait_for_mcp_ready()` en `compare.py`.

### Verificación

- [ ] f1.5-04: Verificar que el servidor MCP responde a `tools/list` con las dos tools registradas.
- [ ] f1.5-05: Ejecutar compare.py con variante v2 y confirmar entrada en metrics.json.

## F1.6 — F1.6 Variante 3: tool-use nativo del provider

### Setup y schemas OpenAI

- [ ] f1.6-01: Crear `variant-3-native-tooluse/tools.py` con `NMAP_SCAN_SCHEMA` y `GOBUSTER_DIR_SCHEMA`.

### Función run_nmap

- [ ] f1.6-02: Implementar `run_nmap(fixture_path: str) -> ToolResult` en `tools.py`.

### Función run_gobuster

- [ ] f1.6-03: Implementar `run_gobuster(fixture_path: str) -> ToolResult` en `tools.py`.

### Verificación

- [ ] f1.6-04: Verificar desde Docker que schemas y funciones run_nmap/run_gobuster funcionan correctamente.

## F1.7 — F1.7 Runner de comparación

### CLI, logging y métricas

- [ ] f1.7-01: Añadir argumentos CLI y funciones `write_jsonl` y `consolidate_metrics` a `compare.py`.

### Funciones de invocación V1 y V3

- [ ] f1.7-02: Implementar `run_v1` y `run_v3` en `compare.py`.

### Función de invocación V2 (MCP)

- [ ] f1.7-03: Implementar `run_v2` con arranque de proceso FastMCP y timeout.

### Flujo principal

- [ ] f1.7-04: Implementar `main()` con selección de variantes, invocación secuencial y consolidación de métricas.

### Verificación

- [ ] f1.7-05: Ejecutar compare.py con variante v1 y verificar JSONL generado.
- [ ] f1.7-06: Ejecutar compare.py con `--variant all --tool all` y verificar metrics.json válido.
- [ ] f1.7-07: Ejecutar compare.py con variante v2 inaccesible y verificar error registrado en metrics.json.

## F1.8 — F1.8 Ejecución y métricas consolidadas

### Soporte de repeticiones en compare.py

- [ ] f1.8-01: Añadir argumento `--repeat N` y campos de media a `consolidate_metrics`.

### Verificación de entorno y ejecución del run real

- [ ] f1.8-02: Ejecutar `--check` y run completo con `--repeat 3` contra TARGET_IP real.
- [ ] f1.8-03: Verificar que metrics.json contiene al menos 6 invocaciones y campos de media.

### Documentación y commit de trazas

- [ ] f1.8-04: Añadir comando del run real en tech-spec.md y commitear trazas.

## F1.9 — F1.9 Reporte comparativo

### Análisis de métricas y token footprint

- [ ] f1.9-01: Calcular duration_ms_mean, tasa de éxito y token footprint para las tres variantes.

### Redacción de report.md

- [ ] f1.9-02: Escribir `outputs/report.md` con hipótesis, tabla de métricas y limitaciones.

### Verificación

- [ ] f1.9-03: Verificar que report.md contiene las tres secciones y referencia a todas las variantes.

## F1.10 — F1.10 Decisión ADR-003

### Análisis del reporte y selección de variante

- [ ] f1.10-01: Identificar la variante ganadora en report.md con criterio de desempate documentado.

### Redacción de driver.md

- [ ] f1.10-02: Escribir `outputs/driver.md` con contrato elegido, evidencia, triggers y riesgos.

### Verificación

- [ ] f1.10-03: Verificar que driver.md contiene las cuatro secciones requeridas.
- [ ] f1.10-04: Verificar `compare.py --check` y que metrics.json tiene al menos dos variantes.

## Log de ejecución

<!-- Los agentes escriben aquí sus registros de ejecución -->
