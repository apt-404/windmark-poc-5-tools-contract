# Plan — F1.9 Reporte comparativo

## Enfoque

Se genera `outputs/report.md` a partir de `traces/metrics.json` y del análisis del código fuente de las tres variantes. El reporte es un documento cuantitativo: hipótesis, tabla de métricas con origen trazable, y limitaciones. Requiere `traces/metrics.json` del run real (F1.8 completada).

## Análisis de métricas y token footprint

- [ ] Leer `traces/metrics.json` y calcular: `duration_ms_mean` por `(variant, tool)` excluyendo invocaciones con `error is not None` (documentar cuántas se excluyeron); tasa de éxito por variante como `invocaciones con error is None / total`; token footprint de schema para V1 (`NmapScanInput.model_json_schema()`), V2 (schema `tools/list` de FastMCP) y V3 (`NMAP_SCAN_SCHEMA`) usando `len(json.dumps(schema)) / 4`; imprimir el dict de resultados como JSON para validar antes de usarlo en el reporte.

## Redacción de report.md

- [ ] Crear `outputs/` si no existe y escribir `outputs/report.md` con las secciones: `## Hipótesis evaluadas` (lista de hipótesis derivadas del tech-spec, p.ej. "V1 tiene menor latencia que V2 dado el overhead del protocolo MCP"), `## Métricas comparativas` (tabla con columnas Variante, Tool, duration_ms_mean, tasa_exito, token_footprint_schema; cada valor con nota al pie referenciando el campo de `metrics.json` o archivo de código del que se extrae), y `## Limitaciones` (las tres limitaciones: startup V2 incluido en latencia, token footprint es estimación estática, LLM mockeado en V3 sin latencia real).

## Tests

- [ ] Crear `tests/test_report.py` con dos funciones pytest derivadas de los Criterios de Aceptación de `requirements.md`: `test_report_contains_required_sections()` lee `outputs/report.md` y verifica que contiene las secciones `## Hipótesis evaluadas`, `## Métricas comparativas` y `## Limitaciones`; `test_report_references_all_variants()` carga `traces/metrics.json`, extrae el conjunto de variantes únicas (`v1`, `v2`, `v3`) y verifica que cada una aparece en el texto de `outputs/report.md`.
- [ ] Ejecutar `pytest tests/test_report.py -v` y confirmar exit code 0.
