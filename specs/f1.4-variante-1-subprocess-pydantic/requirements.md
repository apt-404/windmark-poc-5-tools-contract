# F1.4 — Variante 1: subprocess + Pydantic

## Contexto

V1 es la hipótesis de partida de ADR-003: las tools se implementan como funciones Python puras que invocan el binario con `subprocess.run()`, con input y output tipados mediante los modelos de `shared/models.py`. El JSON schema para tool-use del LLM se genera con `model_json_schema()` sin infraestructura adicional.

## Criterios de aceptación

- [ ] `variant-1-subprocess/nmap_scan.py` define una función `run(input: NmapScanInput) -> ToolResult` que invoca nmap con `subprocess.run()` y devuelve un `ToolResult` válido.
- [ ] `variant-1-subprocess/gobuster_dir.py` define una función `run(input: GobusterDirInput) -> ToolResult` que invoca gobuster con `subprocess.run()` y devuelve un `ToolResult` válido.
- [ ] El campo `extra` de `ToolResult` contiene los datos parseados: `open_ports` y `service_fingerprints` para nmap; `found_paths` y `status_codes` para gobuster.
- [ ] El parseo se hace con regex mínimo sobre `raw_output`; sin librerías de parseo externas.
- [ ] El timeout de subprocess es 30 segundos por tool (hardcoded); si se supera, `ToolResult.error = "timeout"`.
- [ ] Si el subprocess devuelve exit code distinto de 0, el error se captura en `ToolResult.error` y `raw_output` preserva el output parcial.
- [ ] `NmapScanInput.model_json_schema()` y `GobusterDirInput.model_json_schema()` son accesibles desde los módulos de V1 (importados de `shared/models.py`).
- [ ] Ninguna función en V1 importa nada de `variant-2-mcp-stdio/` ni de `variant-3-native-tooluse/`.

## Fuera de alcance

- Librerías de parseo de nmap (python-nmap, libnmap) — parseo con regex sobre texto plano.
- Flag `--output-format json` de gobuster — parseo con regex sobre output texto.
- Timeout configurable por variable de entorno (30 s hardcoded en esta variante).
- Retry o circuit breaker ante fallos del subprocess.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.1 — Contrato de datos compartido | Feature interna | Pendiente |
| F1.2 — Entorno Docker + healthcheck | Feature interna | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Parser nmap | Regex mínimo sobre `raw_output` | python-nmap / libnmap con XML |
| Parser gobuster | Regex mínimo sobre `raw_output` | `gobuster --output-format json` |
| Timeout subprocess | 30 segundos hardcoded | `TOOL_TIMEOUT` configurable por env |
