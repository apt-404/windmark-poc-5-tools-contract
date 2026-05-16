# Reporte comparativo — PoC #5: Contrato de invocación de tools

> [!abstract] Metadata
> | | |
> |---|---|
> | **Status** | 🟡 Pendiente datos (`traces/metrics.json` requiere F1.8) |
> | **Fuente de métricas** | `traces/metrics.json` (run real F1.8) y análisis estático del código fuente |
> | **Analizador** | `report_analysis.py` |

---

## Hipótesis evaluadas

Las hipótesis comparan las tres variantes de contrato de invocación de tools (V1 subprocess+Pydantic, V2 MCP stdio, V3 native tool-use) sobre las dimensiones medidas en `traces/metrics.json`. Se derivan de los ADRs y limitaciones declaradas en `outputs/tech-spec.md`.

- **H1 — Latencia.** V1 tiene menor `duration_ms_mean` que V2 dado el overhead del protocolo MCP y la latencia de startup del subproceso FastMCP incluida en cada invocación de V2 (referencia: `outputs/tech-spec.md` líneas 355–356 y 383).
- **H2 — Latencia V3 vs V1.** V3 tiene `duration_ms_mean` comparable a V1 para tools que ejecutan binarios reales (`nmap_scan`, `gobuster_dir`), porque ambas variantes invocan el tool por import directo sin protocolo intermedio (referencia: `outputs/tech-spec.md` Topología de ejecución, líneas 69–71).
- **H3 — Tasa de éxito.** Las tres variantes alcanzan tasa de éxito similar sobre el mismo set de inputs, dado que comparten el contrato `ToolResult` de `shared/models.py` y los binarios subyacentes. Diferencias en `tasa_exito` se atribuyen a fallos de transporte (stdio en V2) o de parsing de fixtures (V3), no al tool en sí.
- **H4 — Token footprint del schema.** V1 produce el schema más compacto al derivarlo de un modelo Pydantic mínimo (`NmapScanInput`), mientras que V2 (FastMCP `tools/list`) y V3 (`NMAP_SCAN_SCHEMA` en formato OpenAI `tools[]`) añaden envoltorios de protocolo que aumentan el footprint enviado al provider en un uso real.

---

## Métricas comparativas

Los valores de `duration_ms_mean` y `tasa_exito` provienen de `traces/metrics.json` generado por el runner de F1.8 (`compare.py`) y se calculan con `report_analysis.py:analyze()`. El `token_footprint_schema` es una métrica estática derivada del código fuente de cada variante.

| Variante | Tool | duration_ms_mean | tasa_exito | token_footprint_schema |
|---|---|---|---|---|
| v1 | nmap_scan      | _pendiente F1.8_ [^dm] | _pendiente F1.8_ [^sr] | 69 [^tfv1] |
| v1 | gobuster_dir   | _pendiente F1.8_ [^dm] | _pendiente F1.8_ [^sr] | 69 [^tfv1] |
| v2 | nmap_scan      | _pendiente F1.8_ [^dm] | _pendiente F1.8_ [^sr] | 118 [^tfv2] |
| v2 | gobuster_dir   | _pendiente F1.8_ [^dm] | _pendiente F1.8_ [^sr] | 118 [^tfv2] |
| v3 | nmap_scan      | _pendiente F1.8_ [^dm] | _pendiente F1.8_ [^sr] | 131 [^tfv3] |
| v3 | gobuster_dir   | _pendiente F1.8_ [^dm] | _pendiente F1.8_ [^sr] | 131 [^tfv3] |

[^dm]: Calculado por `report_analysis.compute_duration_means()` sobre el campo `results[].duration_ms` de `traces/metrics.json`, agrupando por `(variant, tool)` y excluyendo registros con `error is not None`.
[^sr]: Calculado por `report_analysis.compute_success_rate()` como `count(results[].error is None) / count(results[])` agrupado por `results[].variant` en `traces/metrics.json`.
[^tfv1]: `len(json.dumps(NmapScanInput.model_json_schema())) // 4` calculado sobre `shared/models.py:NmapScanInput`. Mismo schema para ambas tools de V1 dado que el footprint reportado corresponde al schema de `nmap_scan` (referencia común para las tres variantes).
[^tfv2]: `len(json.dumps(tool.to_mcp_tool().model_dump())) // 4` calculado sobre el resultado de `tools/list` del FastMCP server (`variant-2-mcp-stdio/server.py`) para `nmap_scan`.
[^tfv3]: `len(json.dumps(NMAP_SCAN_SCHEMA)) // 4` calculado sobre `variant-3-native-tooluse/tools.py:NMAP_SCAN_SCHEMA` (formato OpenAI `tools[]`).

> Cuando `traces/metrics.json` esté disponible, los valores marcados como _pendiente F1.8_ se obtienen ejecutando `python report_analysis.py --metrics traces/metrics.json`, que imprime `duration_ms_mean`, `success_rate` y `excluded_from_duration_mean` en JSON.

---

## Limitaciones

- **Startup de V2 incluido en la latencia.** Cada run del runner arranca y detiene el proceso FastMCP de V2, por lo que `duration_ms_mean` de V2 incluye el overhead de startup del subproceso. En un escenario de uso real, el MCP server correría continuamente y este coste no se pagaría por invocación (referencia: `outputs/tech-spec.md` líneas 355–356 y 383).
- **Token footprint es una estimación estática.** El valor `token_footprint_schema` se calcula como `len(json.dumps(schema)) // 4` sobre el código fuente, no a partir del tokenizador real del provider. Es una aproximación útil para comparar el tamaño relativo de los schemas entre variantes, pero no equivale al consumo de tokens real de una llamada al LLM (referencia: `specs/f1.9-reporte-comparativo/requirements.md`, decisión "Referencia a tokens").
- **LLM mockeado en V3 sin latencia real.** Las métricas de V3 no incluyen la latencia de generación de tool calls por parte del LLM: lo medido es la latencia de ejecución del tool después de parsear la fixture en `traces/fixtures/`. Un LLM real podría introducir latencia adicional y/o generar tool calls malformados que esta PoC no detecta (referencia: `outputs/tech-spec.md` línea 382).
