# F1.6 — Variante 3: tool-use nativo del provider

## Contexto

V3 simula el ciclo de tool-use del LLM sin llamadas reales a la API. El schema de cada tool se define en formato OpenAI `tools[]` directamente en código Python. V3 lee la fixture pregrabada para obtener los parámetros de invocación, los parsea y ejecuta el binario. Esto mide el path de integración entre el formato de schema del provider y la ejecución del subprocess, sin Pydantic en el camino crítico.

## Criterios de aceptación

- [ ] `variant-3-native-tooluse/tools.py` define el schema de `nmap_scan` y `gobuster_dir` como dicts Python en formato OpenAI `tools[]` (campos: `type`, `function.name`, `function.description`, `function.parameters`).
- [ ] `tools.py` expone las funciones `run_nmap(fixture_path: str) -> ToolResult` y `run_gobuster(fixture_path: str) -> ToolResult`.
- [ ] Cada función lee el `fixture_path`, parsea `function.arguments` con `json.loads()`, ejecuta el binario con `subprocess.run()` y devuelve un `ToolResult` válido.
- [ ] Si el fixture no existe, la función devuelve `ToolResult` con `error = "fixture not found: {fixture_path}"`.
- [ ] El parseo de output usa regex mínimo sobre `raw_output`, reimplementado en `tools.py` sin importar nada de V1 ni V2.
- [ ] El timeout de subprocess es 30 segundos (consistente con V1).
- [ ] `tools.py` no importa Pydantic para construir ni validar los parámetros de invocación; solo los usa para construir el `ToolResult` de retorno.

## Fuera de alcance

- Generación del schema con `model_json_schema()` + conversión (schema escrito a mano).
- Llamadas reales a la API del provider.
- Validación Pydantic de los parámetros extraídos de la fixture.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.1 — Contrato de datos compartido | Feature interna | Pendiente |
| F1.2 — Entorno Docker + healthcheck | Feature interna | Pendiente |
| F1.3 — Fixtures LLM pregrabadas | Feature interna | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Definición del schema OpenAI tools[] | Dict Python escrito a mano en `tools.py` | Generado con `model_json_schema()` + conversión |
| Parseo de output | Reimplementado en `tools.py` con regex (sin importar V1) | Importar lógica de parseo de V1 |
| Estructura de tools.py | `run_nmap(fixture_path)` y `run_gobuster(fixture_path)` separadas | Función genérica `run(fixture_path, tool_name)` |
