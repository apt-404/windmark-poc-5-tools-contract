# F1.9 — Reporte comparativo

## Contexto

`outputs/report.md` documenta las hipótesis evaluadas y las métricas obtenidas del run real, trazables directamente a `traces/metrics.json`. El reporte es el artefacto de evidencia que respalda la decisión de ADR-003 en `driver.md`. Solo incluye datos cuantitativos derivados de las trazas y del análisis del código fuente.

## Criterios de aceptación

- [ ] `outputs/report.md` existe y contiene una sección de hipótesis evaluadas (una por hipótesis de comparación entre variantes).
- [ ] El reporte incluye una tabla comparativa de **latencia media** (`duration_ms_mean`) por variante y tool, calculada a partir de `traces/metrics.json` (3 repeticiones por combinación).
- [ ] El reporte incluye la **tasa de éxito** por variante: invocaciones sin error / total invocaciones del run real.
- [ ] El reporte incluye el **token footprint del schema de tool** por variante: número aproximado de tokens del esquema de definición que se enviaría al provider en un uso real (métrica estática calculada sobre el código, no medida en tiempo de ejecución dado que el LLM está mockeado).
- [ ] Cada métrica está referenciada al dato concreto de `traces/metrics.json` o al archivo de código fuente del que se extrae.
- [ ] El reporte documenta las limitaciones conocidas de las métricas (latencia de startup de V2, LLM mockeado en V3).
- [ ] No contiene afirmaciones que no estén respaldadas por datos del run o del código.

## Fuera de alcance

- Hallazgos cualitativos o de experiencia de desarrollo (van en `driver.md` como contexto de decisión).
- Métricas de tokens reales del LLM (LLM mockeado en esta PoC; se usa token footprint estático del schema).
- Coste de añadir una tool nueva en LoC (puede añadirse como observación en `driver.md` si se considera relevante).

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.8 — Ejecución y métricas consolidadas | Feature interna | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Métricas cuantitativas obligatorias | Latencia media, tasa de éxito, token footprint del schema | Coste en LoC (queda como observación en driver.md) |
| Hallazgos cualitativos | Excluidos del reporte (solo datos cuantitativos) | Sección de observaciones por variante |
| Referencia a tokens | Token footprint estático del schema (sin LLM real) | Tokens medidos en llamadas reales a la API |
