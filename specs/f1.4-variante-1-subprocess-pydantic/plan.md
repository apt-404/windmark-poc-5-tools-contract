# Plan — F1.4 Variante 1: subprocess + Pydantic

## Enfoque

Se implementan dos funciones puras en `variant-1-subprocess/`, una por tool, que aceptan el modelo de input de `shared/models.py`, invocan el binario con `subprocess.run()` con timeout de 30 s, parsean el output con regex mínimo y devuelven un `ToolResult` con los datos estructurados en `extra`. El JSON schema para tool-use se obtiene directamente con `model_json_schema()` sin ninguna capa adicional.

## Módulo nmap_scan

- [x] Crear el directorio `variant-1-subprocess/` con `__init__.py` vacío y `nmap_scan.py` con la función `run(input: NmapScanInput) -> ToolResult` completa: construir el comando `["nmap"] + input.flags + ["-p", input.ports, input.target]`, ejecutar con `subprocess.run(..., capture_output=True, text=True, timeout=30)`, parsear `stdout` con regex `r"(\d+)/tcp\s+open\s+(\S+)"` para extraer `open_ports` y `service_fingerprints`, asignar `extra` y capturar `TimeoutExpired` con `error="timeout"`.

## Módulo gobuster_dir

- [x] Crear `variant-1-subprocess/gobuster_dir.py` con la función `run(input: GobusterDirInput) -> ToolResult` completa: construir el comando gobuster añadiendo `-x` y `",".join(input.extensions)` si `extensions` no está vacío, ejecutar con `subprocess.run()` con timeout 30 s, parsear `stdout` con regex `r"(/\S+)\s+\(Status:\s+(\d+)\)"` para extraer `found_paths` y `status_codes`, asignar `extra` y capturar `TimeoutExpired`.

## Tests

- [ ] Crear `tests/test_variant1.py` con tres funciones pytest derivadas de los Criterios de Aceptación de `requirements.md`: `test_run_nmap_returns_tool_result()` usa `unittest.mock.patch("subprocess.run")` configurado con `returncode=0, stdout="", stderr=""` y verifica que `run_nmap(NmapScanInput(target="127.0.0.1"))` devuelve un `ToolResult` con `exit_code is not None` e `isinstance(extra, dict)`; `test_run_gobuster_returns_tool_result()` hace lo equivalente para `run_gobuster`; `test_run_nmap_timeout_sets_error()` configura `subprocess.run` para lanzar `subprocess.TimeoutExpired` y verifica que `ToolResult.error == "timeout"`.
- [ ] Ejecutar `pytest tests/test_variant1.py -v` y confirmar exit code 0.
