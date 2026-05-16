# Plan — F1.5 Variante 2: MCP server stdio

## Enfoque

Se implementa un servidor FastMCP con transporte stdio que expone `nmap_scan` y `gobuster_dir` usando `@mcp.tool()` con type hints nativos de Python. Las tools en `variant-2-mcp-stdio/tools/` son autónomas. El runner verifica que el servidor está listo enviando un `tools/list` JSON-RPC tras el arranque y esperando respuesta antes de invocar tools. El timeout de arranque está controlado por `MCP_SERVER_TIMEOUT`.

## Setup del módulo

- [ ] Crear el directorio `variant-2-mcp-stdio/` y `variant-2-mcp-stdio/tools/` en la raíz del proyecto.
- [ ] Crear `variant-2-mcp-stdio/__init__.py` y `variant-2-mcp-stdio/tools/__init__.py` vacíos.

## Implementación de tools en variant-2-mcp-stdio/tools/

- [ ] Crear `variant-2-mcp-stdio/tools/nmap_scan.py` con la función `nmap_scan(target: str, ports: str = "1-1000", flags: list[str] = None) -> dict` que invoca nmap con `subprocess.run()`, parsea con regex y devuelve un dict compatible con `ToolResult` (campos: `raw_output`, `exit_code`, `error`, `duration_ms`, `extra`).
- [ ] Crear `variant-2-mcp-stdio/tools/gobuster_dir.py` con la función `gobuster_dir(target: str, wordlist: str, extensions: list[str] = None) -> dict` con la misma estructura de retorno.
- [ ] Reimplementar en cada archivo el parseo con regex mínimo sobre el output de texto del binario (sin importar nada de `variant-1-subprocess/`).

## Implementación del servidor FastMCP

- [ ] Crear `variant-2-mcp-stdio/server.py` que instancie `mcp = FastMCP("windmark-poc5-v2")`.
- [ ] Registrar las dos tools con `@mcp.tool()` llamando a las funciones de `variant-2-mcp-stdio/tools/`.
- [ ] Configurar el servidor para arrancar con `mcp.run(transport="stdio")` en el bloque `if __name__ == "__main__"`.

## Lógica de arranque y healthcheck en el runner (stub)

- [ ] Añadir en `compare.py` la función `start_mcp_server() -> subprocess.Popen` que arranca `python variant-2-mcp-stdio/server.py` con `subprocess.Popen(..., stdin=PIPE, stdout=PIPE, stderr=PIPE)`.
- [ ] Implementar `wait_for_mcp_ready(proc, timeout_s)` que envía un `tools/list` JSON-RPC por stdin del proceso y espera la respuesta en stdout; devuelve `True` si responde antes de `timeout_s`, `False` en caso contrario.
- [ ] Si `wait_for_mcp_ready` devuelve `False`, marcar V2 como error en `ToolResult` y continuar con las otras variantes.

## Verificación

- [ ] Desde el contenedor Docker, ejecutar `python variant-2-mcp-stdio/server.py` en un terminal y en otro enviar manualmente un `tools/list` JSON-RPC por stdin; verificar que el servidor responde con la lista de tools.
- [ ] Ejecutar `python compare.py --variant v2 --target 127.0.0.1` y verificar que el servidor arranca, responde al `tools/list` y la invocación de tool devuelve un `ToolResult` sin excepción.
