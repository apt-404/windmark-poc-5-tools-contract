# Plan — F1.6 Variante 3: tool-use nativo del provider

## Enfoque

Se implementa `variant-3-native-tooluse/tools.py` con los schemas de las dos tools en formato OpenAI `tools[]` escritos a mano como dicts Python, y dos funciones de ejecución (`run_nmap`, `run_gobuster`) que leen la fixture JSON, extraen los parámetros con `json.loads()`, ejecutan el binario con `subprocess.run()` y devuelven un `ToolResult`. No se usa Pydantic para construir ni validar los parámetros de invocación; solo para construir el objeto de retorno.

## Setup del módulo

- [ ] Crear el directorio `variant-3-native-tooluse/` en la raíz del proyecto.
- [ ] Crear `variant-3-native-tooluse/__init__.py` vacío.

## Definición de schemas OpenAI tools[]

- [ ] Crear `variant-3-native-tooluse/tools.py` con el dict `NMAP_SCAN_SCHEMA` en formato OpenAI: `{"type": "function", "function": {"name": "nmap_scan", "description": "...", "parameters": {"type": "object", "properties": {"target": ..., "ports": ..., "flags": ...}, "required": ["target"]}}}`.
- [ ] Añadir el dict `GOBUSTER_DIR_SCHEMA` análogo para `gobuster_dir` con los campos `target`, `wordlist` y `extensions`.

## Implementación de run_nmap

- [ ] Implementar `run_nmap(fixture_path: str) -> ToolResult` que: abre `fixture_path` con `json.load()` y captura `FileNotFoundError` devolviendo `ToolResult` con `error="fixture not found: {fixture_path}"`; extrae `params = json.loads(data["function"]["arguments"])`; construye el comando nmap con `params["target"]`, `params.get("ports", "1-1000")` y `params.get("flags", ["-sV"])`; ejecuta con `subprocess.run()` con timeout 30 s; parsea output con regex; devuelve `ToolResult`.
- [ ] Capturar `subprocess.TimeoutExpired` y devolver `ToolResult` con `error="timeout"`.

## Implementación de run_gobuster

- [ ] Implementar `run_gobuster(fixture_path: str) -> ToolResult` con la misma estructura: leer fixture, extraer `target`, `wordlist` y `extensions` con `params.get()`; construir y ejecutar el comando gobuster; parsear output; devolver `ToolResult`.
- [ ] Capturar `subprocess.TimeoutExpired` y devolver `ToolResult` con `error="timeout"`.

## Verificación

- [ ] Ejecutar `python -c "from variant_3_native_tooluse.tools import run_nmap; r = run_nmap('traces/fixtures/nmap_scan.json'); print(r.exit_code, r.error)"` desde el contenedor Docker y verificar que devuelve `ToolResult` sin excepción.
- [ ] Ejecutar `run_nmap('traces/fixtures/no_existe.json')` y verificar que devuelve `ToolResult` con `error` que contiene "fixture not found".
- [ ] Verificar que `NMAP_SCAN_SCHEMA` y `GOBUSTER_DIR_SCHEMA` son dicts Python válidos con los campos `type`, `function.name`, `function.description` y `function.parameters`.
