# F1.5 — Variante 2: MCP server stdio

## Contexto

V2 expone las mismas dos tools a través de un servidor FastMCP con transporte stdio. El runner arranca el servidor como subproceso hijo, actúa como cliente MCP y recibe los resultados vía JSON-RPC. Esta variante mide el overhead real del protocolo MCP respecto a la invocación directa en proceso de V1.

## Criterios de aceptación

- [ ] `variant-2-mcp-stdio/server.py` arranca un servidor FastMCP que expone las tools `nmap_scan` y `gobuster_dir` con `@mcp.tool()`.
- [ ] Las tools están registradas con type hints nativos de Python (sin Pydantic en el decorador); FastMCP infiere el schema.
- [ ] `variant-2-mcp-stdio/tools/nmap_scan.py` y `variant-2-mcp-stdio/tools/gobuster_dir.py` implementan las tools de forma autónoma, sin importar nada de `variant-1-subprocess/`.
- [ ] El parseo de output en V2 usa regex mínimo sobre `raw_output`, igual que V1, reimplementado en el módulo de V2.
- [ ] Tras el arranque, el servidor responde a un `tools/list` JSON-RPC para confirmar que está listo; el runner espera esta respuesta antes de invocar tools.
- [ ] Si el servidor no responde al `tools/list` en `MCP_SERVER_TIMEOUT` segundos, el runner marca V2 como error y continúa.
- [ ] Cada invocación de tool devuelve un `ToolResult` válido (serializado a JSON para el transporte MCP y deserializado en el runner).
- [ ] El servidor no importa nada de `variant-1-subprocess/` ni de `variant-3-native-tooluse/`.

## Fuera de alcance

- Transporte HTTP/SSE (solo stdio en esta PoC).
- Reutilización del código de parseo de V1.
- Múltiples instancias del servidor MCP (1 server por run del runner).
- Autenticación o TLS en el servidor MCP.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.1 — Contrato de datos compartido | Feature interna | Pendiente |
| F1.2 — Entorno Docker + healthcheck | Feature interna | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Reutilización de parseo | Reimplementar en V2 (sin importar V1) | Importar funciones `run()` de V1 |
| Registro de tools en FastMCP | `@mcp.tool()` con type hints nativos de Python | `@mcp.tool()` con modelos Pydantic de `shared/` |
| Healthcheck del servidor | `tools/list` JSON-RPC tras el arranque; runner espera respuesta | Solo timeout sin verificación activa |
