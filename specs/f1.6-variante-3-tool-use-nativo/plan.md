# Plan — F1.6 Variante 3: tool-use nativo del provider

## Enfoque

Se implementa `variant-3-native-tooluse/tools.py` con los schemas de las dos tools en formato OpenAI `tools[]` escritos a mano como dicts Python, y dos funciones de ejecución (`run_nmap`, `run_gobuster`) que leen la fixture JSON, extraen los parámetros con `json.loads()`, ejecutan el binario con `subprocess.run()` y devuelven un `ToolResult`. No se usa Pydantic para construir ni validar los parámetros de invocación; solo para construir el objeto de retorno.

## Setup y schemas OpenAI

- [x] Crear el directorio `variant-3-native-tooluse/` con `__init__.py` vacío y `tools.py` con los dos dicts de schema en formato OpenAI: `NMAP_SCAN_SCHEMA` (`{"type": "function", "function": {"name": "nmap_scan", "description": "...", "parameters": {"type": "object", "properties": {"target": ..., "ports": ..., "flags": ...}, "required": ["target"]}}}`) y `GOBUSTER_DIR_SCHEMA` análogo con campos `target`, `wordlist` y `extensions`.

## Función run_nmap

- [x] Implementar `run_nmap(fixture_path: str) -> ToolResult` en `tools.py`: abrir fixture con `json.load()` capturando `FileNotFoundError` (devolver `ToolResult` con `error=f"fixture not found: {fixture_path}"`); extraer `params = json.loads(data["function"]["arguments"])`; construir y ejecutar el comando nmap con timeout 30 s; parsear output con regex; devolver `ToolResult`; capturar `TimeoutExpired` con `error="timeout"`.

## Función run_gobuster

- [x] Implementar `run_gobuster(fixture_path: str) -> ToolResult` en `tools.py` con la misma estructura: leer fixture, extraer `target`, `wordlist` y `extensions` con `params.get()`; construir y ejecutar el comando gobuster con timeout 30 s; parsear output con regex; devolver `ToolResult`; capturar `TimeoutExpired`.

## Tests

- [ ] Crear `tests/test_variant3.py` con tres funciones pytest derivadas de los Criterios de Aceptación de `requirements.md`: `test_nmap_scan_schema_format()` verifica que `NMAP_SCAN_SCHEMA['type'] == 'function'` y que `'parameters'` está en `NMAP_SCAN_SCHEMA['function']`; `test_run_nmap_with_fixture()` usa `unittest.mock.patch("subprocess.run")` con `returncode=0, stdout=""` y llama a `run_nmap("traces/fixtures/nmap_scan.json")` verificando que el resultado es `ToolResult` con `exit_code is not None`; `test_run_nmap_missing_fixture_returns_error()` llama a `run_nmap("traces/fixtures/no_existe.json")` sin mock y verifica que `ToolResult.error` contiene `"fixture not found"`.
- [ ] Ejecutar `pytest tests/test_variant3.py -v` y confirmar exit code 0.
