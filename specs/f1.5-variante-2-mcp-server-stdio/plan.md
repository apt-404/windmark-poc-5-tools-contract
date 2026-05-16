# Plan — F1.5 Variante 2: MCP server stdio

## Enfoque

Se implementa un servidor FastMCP con transporte stdio que expone `nmap_scan` y `gobuster_dir` usando `@mcp.tool()` con type hints nativos de Python. Las tools en `variant-2-mcp-stdio/tools/` son autónomas. El runner verifica que el servidor está listo enviando un `tools/list` JSON-RPC tras el arranque y esperando respuesta antes de invocar tools. El timeout de arranque está controlado por `MCP_SERVER_TIMEOUT`.

## Tools MCP

- [ ] Crear el directorio `variant-2-mcp-stdio/` y `variant-2-mcp-stdio/tools/` con sus respectivos `__init__.py` vacíos; crear `variant-2-mcp-stdio/tools/nmap_scan.py` con `nmap_scan(target: str, ports: str = "1-1000", flags: list[str] = None) -> dict` y `variant-2-mcp-stdio/tools/gobuster_dir.py` con `gobuster_dir(target: str, wordlist: str, extensions: list[str] = None) -> dict`, cada uno con `subprocess.run()`, parseo regex y retorno de dict compatible con los campos de `ToolResult`.

## Servidor FastMCP

- [ ] Crear `variant-2-mcp-stdio/server.py` que instancie `mcp = FastMCP("windmark-poc5-v2")`, registre las dos tools con `@mcp.tool()` llamando a las funciones de `tools/`, y arranque con `mcp.run(transport="stdio")` en el bloque `if __name__ == "__main__"`.

## Integración en compare.py

- [ ] Añadir en `compare.py` las funciones `start_mcp_server() -> subprocess.Popen` (arranca `python variant-2-mcp-stdio/server.py` con `stdin=PIPE, stdout=PIPE, stderr=PIPE`) y `wait_for_mcp_ready(proc, timeout_s) -> bool` (envía `{"jsonrpc":"2.0","method":"tools/list","id":1}` por stdin y lee stdout con timeout; devuelve `True` si responde antes de `timeout_s`, `False` en caso contrario); si devuelve `False`, devolver `ToolResult` con `error="mcp_server_timeout"`.

## Verificación

- [ ] Ejecutar `python -c "import subprocess, json, time; p = subprocess.Popen(['python', 'variant-2-mcp-stdio/server.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE); p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'tools/list','id':1}).encode()+b'\n'); p.stdin.flush(); time.sleep(2); line = p.stdout.readline(); p.terminate(); resp = json.loads(line); tools = [t['name'] for t in resp['result']['tools']]; assert 'nmap_scan' in tools and 'gobuster_dir' in tools; print('OK')"` y confirmar `OK` con código de salida 0.
- [ ] Ejecutar `python compare.py --variant v2 --tool nmap_scan --target 127.0.0.1` y confirmar que el proceso termina sin excepción no capturada y que `traces/metrics.json` contiene al menos una entrada con `"variant": "v2"`.
