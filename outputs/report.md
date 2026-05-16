# Reporte comparativo — PoC #5: Contrato de invocación de tools

> [!abstract] Metadata
> | | |
> |---|---|
> | **Status** | 🟢 Datos reales disponibles (run HTB 2026-05-16) |
> | **Fuente de métricas** | `traces/metrics.json` (run real contra HTB Starting Point) y análisis estático del código fuente |
> | **Analizador** | `report_analysis.py` |

---

## Condiciones del run

| Parámetro | Valor |
|---|---|
| Fecha | 2026-05-16 |
| Target | `10.129.160.94` — **Meow** (HTB Starting Point, EU Starting Point 2) |
| Máquina | Linux · Very Easy · Telnet con credenciales por defecto · enfocada en enumeración básica |
| Repeticiones | 3 por combinación (variante × tool) |
| Entorno | WSL2 (Ubuntu) + OpenVPN tun1 (UDP 1337) |
| nmap | 7.94SVN |
| gobuster | 3.6 |
| Wordlist | `~/wordlists/common.txt` (dirb common, descargado de GitHub) |
| Flags nmap | `-Pn -sV` (default `shared/models.py` y fixture V3 desde este run) |

---

## Hipótesis evaluadas

Las hipótesis comparan las tres variantes de contrato de invocación de tools (V1 subprocess+Pydantic, V2 MCP stdio, V3 native tool-use) sobre las dimensiones medidas en `traces/metrics.json`. Se derivan de los ADRs y limitaciones declaradas en `outputs/tech-spec.md`.

- **H1 — Latencia.** V1 tiene menor `duration_ms_mean` que V2 dado el overhead del protocolo MCP y la latencia de startup del subproceso FastMCP incluida en cada invocación de V2 (referencia: `outputs/tech-spec.md` líneas 355–356 y 383).
  > **Resultado: CONFIRMADA.** V1=10 080.6 ms vs V2=12 845.5 ms en `nmap_scan`. V2 es un 27 % más lento; el overhead de startup del proceso FastMCP por invocación es ~2.8 s. No evaluable en `gobuster_dir` (todas las variantes fallan por infra — puerto 80 cerrado en el target).

- **H2 — Latencia V3 vs V1.** V3 tiene `duration_ms_mean` comparable a V1 para tools que ejecutan binarios reales (`nmap_scan`, `gobuster_dir`), porque ambas variantes invocan el tool por import directo sin protocolo intermedio (referencia: `outputs/tech-spec.md` Topología de ejecución, líneas 69–71).
  > **Resultado: NO EVALUABLE.** V3 nmap agota `TIMEOUT_SECONDS=30` en `tools.py` con `-Pn -sV -p 1-1000` sobre target remoto (0/3, todas las repeticiones timeout). V3 gobuster llega al target (31.6 ms, `connection refused`) pero falla por infra igual que V1/V2 — no es comparable en latencia de scan real.

- **H3 — Tasa de éxito.** Las tres variantes alcanzan tasa de éxito similar sobre el mismo set de inputs, dado que comparten el contrato `ToolResult` de `shared/models.py` y los binarios subyacentes. Diferencias en `tasa_exito` se atribuyen a fallos de transporte (stdio en V2) o de parsing de fixtures (V3), no al tool en sí.
  > **Resultado: REFUTADA.** `nmap_scan`: V1=100 % (3/3), V2=33 % (1/3 — 2 timeouts MCP), V3=0 % (3/3 timeout de subprocess). Las tasas difieren significativamente. V2 muestra menor fiabilidad por timeouts del proceso FastMCP; V3 agota el timeout de 30 s del runner. `gobuster_dir`: todas las variantes 0 % por infraestructura (puerto 80 cerrado en el target), no atribuible al contrato de tool.

- **H4 — Token footprint del schema.** V1 produce el schema más compacto al derivarlo de un modelo Pydantic mínimo (`NmapScanInput`), mientras que V2 (FastMCP `tools/list`) y V3 (`NMAP_SCAN_SCHEMA` en formato OpenAI `tools[]`) añaden envoltorios de protocolo que aumentan el footprint enviado al provider en un uso real.
  > **Resultado: CONFIRMADA** (métrica estática, no depende del run). 69 < 118 < 131 tokens estimados.

---

## Métricas comparativas

Los valores de `duration_ms_mean` y `tasa_exito` provienen de `traces/metrics.json` generado por el runner de F1.8 (`compare.py`) y se calculan con `report_analysis.py:analyze()`. El `token_footprint_schema` es una métrica estática derivada del código fuente de cada variante.

| Variante | Tool | duration_ms_mean | tasa_exito | token_footprint_schema |
|---|---|---|---|---|
| v1 | nmap_scan      | 10 080.6 ms [^dm] | 100 % (3/3) [^sr] | 69 [^tfv1] |
| v1 | gobuster_dir   | 6 683.2 ms [^dm] [^gb-fail] | 0 % (0/3) [^gb-fail] | 69 [^tfv1] |
| v2 | nmap_scan      | 12 845.5 ms [^dm] | 33 % (1/3) [^v2-timeout] | 118 [^tfv2] |
| v2 | gobuster_dir   | 5 341.9 ms [^dm] [^gb-fail] | 0 % (0/3) [^gb-fail] | 118 [^tfv2] |
| v3 | nmap_scan      | 30 025.8 ms [^dm] [^v3-timeout] | 0 % (0/3) [^v3-timeout] | 131 [^tfv3] |
| v3 | gobuster_dir   | 31.6 ms [^dm] [^gb-fail] | 0 % (0/3) [^gb-fail] | 131 [^tfv3] |

[^dm]: Media de `results[].duration_ms` de `traces/metrics.json` agrupada por `(variant, tool)` sobre 3 repeticiones del run 2026-05-16 con flags `-Pn -sV`.
[^sr]: `count(error is None) / count(total)` agrupado por `(variant, tool)` sobre las 3 repeticiones del run 2026-05-16.
[^gb-fail]: `gobuster_dir` falla en todas las variantes porque el puerto 80 está cerrado en el target HTB (confirmado por nmap: 999 puertos cerrados). Es fallo de infraestructura, no del contrato de tool. Latencias reflejan el tiempo hasta recibir `connection refused` o agotar el timeout HTTP de gobuster. La media de V1 (6 683.2 ms) está sesgada por 2 timeouts (10 s) + 1 refused rápido (38 ms).
[^v2-timeout]: 2 de 3 repeticiones devolvieron `v2_no_response` en nmap (timeout del runner MCP a los 10 s). Causa: `compare.py:run_v2` hardcodea `flags=["-sV"]` sin `-Pn` → nmap intenta ICMP, el target lo bloquea y tarda >10 s. La 1 repetición exitosa en V2 nmap reportó "Host seems down" (exit_code=0 pero sin scan real).
[^v3-timeout]: V3 `nmap_scan` agota `TIMEOUT_SECONDS=30` definido en `variant-3-native-tooluse/tools.py`. Con `-Pn -sV -p 1-1000` sobre un target remoto, nmap supera los 30 s de timeout del subprocess. Las 3 repeticiones alcanzaron exactamente 30 024–30 029 ms.
[^tfv1]: `len(json.dumps(NmapScanInput.model_json_schema())) // 4` sobre `shared/models.py:NmapScanInput`.
[^tfv2]: `len(json.dumps(tool.to_mcp_tool().model_dump())) // 4` sobre `tools/list` del FastMCP server (`variant-2-mcp-stdio/server.py`) para `nmap_scan`.
[^tfv3]: `len(json.dumps(NMAP_SCAN_SCHEMA)) // 4` sobre `variant-3-native-tooluse/tools.py:NMAP_SCAN_SCHEMA` (formato OpenAI `tools[]`).

---

## Limitaciones

- **Startup de V2 incluido en la latencia.** Cada run del runner arranca y detiene el proceso FastMCP de V2, por lo que `duration_ms_mean` de V2 incluye el overhead de startup del subproceso. En un escenario de uso real, el MCP server correría continuamente y este coste no se pagaría por invocación (referencia: `outputs/tech-spec.md` líneas 355–356 y 383).
- **Token footprint es una estimación estática.** El valor `token_footprint_schema` se calcula como `len(json.dumps(schema)) // 4` sobre el código fuente, no a partir del tokenizador real del provider. Es una aproximación útil para comparar el tamaño relativo de los schemas entre variantes, pero no equivale al consumo de tokens real de una llamada al LLM (referencia: `specs/f1.9-reporte-comparativo/requirements.md`, decisión "Referencia a tokens").
- **LLM mockeado en V3 sin latencia real.** Las métricas de V3 no incluyen la latencia de generación de tool calls por parte del LLM: lo medido es la latencia de ejecución del tool después de parsear la fixture en `traces/fixtures/`. Un LLM real podría introducir latencia adicional y/o generar tool calls malformados que esta PoC no detecta (referencia: `outputs/tech-spec.md` línea 382).
