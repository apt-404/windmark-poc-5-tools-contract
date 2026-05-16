# Plan — F1.9 Reporte comparativo

## Enfoque

Se redacta `outputs/report.md` a partir de `traces/metrics.json` y del análisis del código fuente de las tres variantes. El reporte es un documento cuantitativo: hipótesis, tabla de métricas con origen trazable, y limitaciones. No se redacta hasta tener `traces/metrics.json` del run real (F1.8 completada).

## Extracción de métricas de metrics.json

- [ ] Abrir `traces/metrics.json` y agrupar los resultados por `(variant, tool)`.
- [ ] Calcular `duration_ms_mean` por `(variant, tool)` como la media de las 3 repeticiones (excluir invocaciones con `error is not None` del cálculo de media; documentar cuántas se excluyeron).
- [ ] Calcular la tasa de éxito por variante: `invocaciones con error is None / total invocaciones` en el run.

## Cálculo del token footprint de schema

- [ ] Abrir el archivo de schema de cada variante y calcular el número aproximado de tokens de la definición de tool (una aproximación válida: `len(json.dumps(schema)) / 4` caracteres / tokens).
- [ ] Registrar el footprint de `NmapScanInput.model_json_schema()` (V1), del schema `tools/list` que devuelve FastMCP en V2 y de `NMAP_SCAN_SCHEMA` en V3; ídem para gobuster.

## Redacción de report.md

- [ ] Crear `outputs/report.md` con sección `## Hipótesis evaluadas` que liste las hipótesis de comparación (p.ej. "V1 tiene menor latencia que V2 dado el overhead del protocolo MCP").
- [ ] Añadir sección `## Métricas comparativas` con tabla: columnas `Variante`, `Tool`, `duration_ms_mean`, `tasa_exito`, `token_footprint_schema`; filas por `(variante, tool)`.
- [ ] Añadir sección `## Limitaciones` que documente: (a) latencia de V2 incluye startup del servidor; (b) token footprint es una estimación estática, no un conteo real de tokens de la API; (c) LLM mockeado en V3, sin latencia real de generación de tool calls.
- [ ] Para cada valor de la tabla, añadir una nota al pie con la referencia al campo de `metrics.json` o al archivo de código del que se extrae.

## Verificación

- [ ] Verificar que cada fila de la tabla de métricas tiene al menos un valor trazable a `traces/metrics.json` o a un archivo de código fuente.
- [ ] Verificar que la sección de Limitaciones menciona las tres limitaciones conocidas del tech-spec (startup V2, token footprint estático, LLM mockeado).
- [ ] Verificar que `outputs/report.md` no contiene afirmaciones sin respaldo en datos (revisar cada afirmación frente a metrics.json).
