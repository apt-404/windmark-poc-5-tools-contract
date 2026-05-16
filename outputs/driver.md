# Driver — ADR-003: Contrato de invocación de tools

> [!abstract] Metadata
> | | |
> |---|---|
> | **ADR** | ADR-003 (cerrado por esta PoC) |
> | **Fuente de evidencia** | `outputs/report.md` y `traces/metrics.json` |
> | **Análisis previo** | `specs/f1.10-decision-adr-003/analysis.md` |

---

## Contrato elegido

**V1 — subprocess + Pydantic.** V1 obtiene la combinación más favorable de las tres dimensiones medidas: empata con V3 y gana a V2 en latencia según H1 y H2 (`report.md` § *Hipótesis evaluadas*, líneas 16–17), empata con V2 y V3 en tasa de éxito según H3 (`report.md` línea 18) y gana de forma estricta en token footprint con 69 frente a 118 (V2) y 131 (V3) según la tabla de § *Métricas comparativas* (`report.md` líneas 27–34). El desempate frente a V3 en latencia lo resuelve el footprint (V1 estrictamente menor) reforzado por simplicidad operativa y portabilidad: V1 no acopla el contrato a ningún protocolo concreto y el schema Pydantic mínimo (`shared/models.py:NmapScanInput`, ver `report.md` nota `[^tfv1]`) es reutilizable independientemente del transporte.

---

## Evidencia

Métricas de la variante elegida (V1) sobre las dos tools del catálogo. Fuente: `outputs/report.md` § *Métricas comparativas* (líneas 27–34).

| Tool | duration_ms_mean | tasa_exito | token_footprint_schema |
|---|---|---|---|
| nmap_scan    | _pendiente F1.8_ [^dm-v1] | _pendiente F1.8_ [^sr-v1] | 69 [^tf-v1] |
| gobuster_dir | _pendiente F1.8_ [^dm-v1] | _pendiente F1.8_ [^sr-v1] | 69 [^tf-v1] |

[^dm-v1]: Campo derivado de `traces/metrics.json` → `results[].duration_ms` filtrado por `results[].variant == "v1"` y agrupado por `results[].tool`, excluyendo registros con `error is not None`. Calculado por `report_analysis.compute_duration_means()` (`report.md` nota `[^dm]`).
[^sr-v1]: Campo derivado de `traces/metrics.json` → `count(results[].error is None) / count(results[])` con filtro `results[].variant == "v1"`. Calculado por `report_analysis.compute_success_rate()` (`report.md` nota `[^sr]`).
[^tf-v1]: Métrica estática `len(json.dumps(NmapScanInput.model_json_schema())) // 4` sobre `shared/models.py:NmapScanInput` (`report.md` nota `[^tfv1]`). No proviene de `traces/metrics.json`: es estimación derivada del código fuente del contrato de V1.

---

## Triggers de upgrade a MCP

ADR-003 mantiene V1 mientras se cumplan los tres criterios siguientes. La activación de **cualquiera** de ellos obliga a reevaluar el contrato hacia MCP:

- **Segundo cliente independiente del catálogo de tools.** Se activa cuando un consumidor distinto del agente orquestador del MVP necesita invocar las mismas tools del catálogo. Cuenta como segundo cliente: (a) un segundo proceso Python con imports propios que no comparta el runtime del agente actual, o (b) un servicio externo (no-Python o fuera del host del MVP) que consuma las tools por un transporte de red. No cuenta como segundo cliente: un nuevo módulo importado dentro del mismo proceso del agente actual.
- **Blast radius de la tool por encima del umbral del host compartido.** Se activa cuando se incorpora al catálogo una tool cuyo perfil de impacto excede lo aceptable en el host del agente. Criterio verificable: (a) tool que requiere capacidades del kernel o privilegios elevados (root, `CAP_NET_ADMIN`, `CAP_SYS_ADMIN`), (b) tool con acceso de escritura al filesystem fuera de un directorio de trabajo acotado, o (c) tool que crea procesos hijos cuyo aislamiento de fallos no puede garantizarse en el mismo host. Cualquiera de las tres condiciones justifica un contenedor separado y, con él, un protocolo entre procesos como MCP.
- **Demanda explícita de protocolo MCP.** Se activa cuando un cliente externo del MVP exige integrar las tools por el protocolo MCP estándar como condición de adopción. Criterio verificable: requerimiento documentado de un consumidor real (no hipotético) que especifique MCP como contrato de integración. La demanda interna (preferencia del equipo) no cuenta; solo cuenta una demanda externa que bloquee la adopción del producto sin MCP.

---

## Riesgos asumidos

Riesgos derivados de las limitaciones de la PoC (`outputs/tech-spec.md` § *Known Limitations*, líneas 380–385, y `outputs/report.md` § *Limitaciones*, líneas 46–50) que se asumen al cerrar ADR-003 con V1:

- **Token footprint medido es una estimación estática.** El valor `token_footprint_schema = 69` para V1 se calcula como `len(json.dumps(schema)) // 4` sobre el código fuente, no con el tokenizador real del provider (`report.md` línea 49). Riesgo asumido: la ventaja de V1 sobre V2 (118) y V3 (131) en footprint podría comprimirse al medirla con el tokenizador real, aunque la diferencia relativa entre schemas se mantendría.
- **Comparativa frente a V3 hecha sin LLM real.** Las métricas de V3 medidas en la PoC no incluyen latencia de generación de tool calls por parte del LLM (`tech-spec.md` línea 382; `report.md` línea 50). Riesgo asumido: la decisión de no adoptar V3 se basa en footprint y portabilidad, no en latencia real con LLM en el loop; un escenario futuro con tool-use nativo en producción podría exhibir características no observadas aquí.
- **V1 no expone protocolo de descubrimiento de tools.** Al no acoplarse a MCP, V1 carece de un endpoint estándar tipo `tools/list` (`tech-spec.md` ADR-003, línea 374). Riesgo asumido: cualquier consumidor adicional del catálogo (ver trigger «Segundo cliente independiente») deberá conocer el contrato Pydantic por import directo o por documentación interna hasta que se active el upgrade a MCP.
- **Fixtures de V3 obsolescibles no afectan a V1, pero limitan la comparación.** Las fixtures de Claude CLI usadas en V3 reflejan el formato de respuesta de la API en el momento de la grabación (`tech-spec.md` línea 385). Riesgo asumido: la comparación entre V1 y V3 podría dejar de ser válida si el formato `tools[]` del provider cambia; la decisión por V1 se sostiene aunque esa comparación quede desactualizada, dado que se apoya principalmente en footprint y portabilidad.
