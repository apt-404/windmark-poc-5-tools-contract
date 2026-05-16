# Análisis de `outputs/report.md` y selección de variante

## Métricas por variante

Fuente: `outputs/report.md` § *Métricas comparativas* (líneas 23–34).

| Variante | duration_ms_mean | tasa_exito | token_footprint_schema |
|---|---|---|---|
| V1 (subprocess+Pydantic) | pendiente F1.8 | pendiente F1.8 | **69** |
| V2 (MCP stdio) | pendiente F1.8 | pendiente F1.8 | 118 |
| V3 (native tool-use) | pendiente F1.8 | pendiente F1.8 | 131 |

Los valores de `duration_ms_mean` y `tasa_exito` aparecen como _pendiente F1.8_ en `report.md` líneas 29–34, por lo que el ranking en esas dos dimensiones se deriva de las hipótesis declaradas en § *Hipótesis evaluadas* (líneas 12–19), que están a su vez respaldadas por referencias a `outputs/tech-spec.md`.

## Ranking por dimensión

- **Latencia media (`duration_ms_mean`)** — V1 ≤ V2 según H1 (`report.md` línea 16: «V1 tiene menor `duration_ms_mean` que V2 dado el overhead del protocolo MCP y la latencia de startup del subproceso FastMCP»). V1 ≈ V3 según H2 (`report.md` línea 17: «V3 tiene `duration_ms_mean` comparable a V1 […] sin protocolo intermedio»). ⇒ V1 y V3 empatan como mejores; V2 queda detrás.
- **Tasa de éxito (`tasa_exito`)** — V1 ≈ V2 ≈ V3 según H3 (`report.md` línea 18: «Las tres variantes alcanzan tasa de éxito similar […] dado que comparten el contrato `ToolResult`»). ⇒ Empate triple, no discrimina.
- **Token footprint del schema (`token_footprint_schema`)** — V1 (69) < V2 (118) < V3 (131), según la tabla de § *Métricas comparativas* (`report.md` líneas 29–34) y H4 (`report.md` línea 19: «V1 produce el schema más compacto al derivarlo de un modelo Pydantic mínimo»). ⇒ V1 gana de forma estricta.

## Variante elegida

**V1 — subprocess + Pydantic.**

Combinación más favorable de las tres dimensiones:

- Empata con V3 y gana a V2 en latencia (H1, H2 en `report.md` líneas 16–17).
- Empata con V2 y V3 en tasa de éxito (H3 en `report.md` línea 18).
- Gana de forma estricta a V2 y V3 en token footprint (tabla § *Métricas comparativas* `report.md` líneas 29–34 y H4 en línea 19).

## Argumento de desempate V1 vs V3 (latencia)

V1 y V3 quedan empatadas en latencia (H2), pero el desempate global lo resuelve la dimensión de token footprint, donde V1 (69) es estrictamente menor que V3 (131). Si además se aplican los criterios de simplicidad operativa y portabilidad del tech-spec:

- **Simplicidad operativa**: V1 invoca el tool por subprocess sin requerir un LLM real ni protocolo intermedio. V3 (native tool-use) depende del formato `tools[]` del provider y, en la PoC, está mockeado con fixtures (`report.md` línea 50: «LLM mockeado en V3 sin latencia real»), lo que implica que su comportamiento en producción es menos verificable que el de V1.
- **Portabilidad**: V1 no acopla el contrato a ningún protocolo concreto (ni MCP ni el formato nativo del provider). El schema Pydantic mínimo (`shared/models.py:NmapScanInput`, ver `report.md` nota `[^tfv1]`) es reutilizable independientemente del transporte.

## Referencias exactas a `report.md`

- § *Hipótesis evaluadas*: líneas 12–19 (H1, H2, H3, H4).
- § *Métricas comparativas*: líneas 23–34 (tabla) y notas al pie `[^tfv1]`, `[^tfv2]`, `[^tfv3]` (líneas 38–40).
- § *Limitaciones*: línea 48 (startup de V2 incluido en latencia), línea 49 (token footprint estático), línea 50 (LLM mockeado en V3) — informan los riesgos asumidos por la elección de V1.
