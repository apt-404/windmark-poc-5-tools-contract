# Plan — F1.9 Reporte comparativo

## Enfoque

Se genera `outputs/report.md` a partir de `traces/metrics.json` y del análisis del código fuente de las tres variantes. El reporte es un documento cuantitativo: hipótesis, tabla de métricas con origen trazable, y limitaciones. Requiere `traces/metrics.json` del run real (F1.8 completada).

## Análisis de métricas y token footprint

- [ ] Leer `traces/metrics.json` y calcular: `duration_ms_mean` por `(variant, tool)` excluyendo invocaciones con `error is not None` (documentar cuántas se excluyeron); tasa de éxito por variante como `invocaciones con error is None / total`; token footprint de schema para V1 (`NmapScanInput.model_json_schema()`), V2 (schema `tools/list` de FastMCP) y V3 (`NMAP_SCAN_SCHEMA`) usando `len(json.dumps(schema)) / 4`; imprimir el dict de resultados como JSON para validar antes de usarlo en el reporte.

## Redacción de report.md

- [ ] Crear `outputs/` si no existe y escribir `outputs/report.md` con las secciones: `## Hipótesis evaluadas` (lista de hipótesis derivadas del tech-spec, p.ej. "V1 tiene menor latencia que V2 dado el overhead del protocolo MCP"), `## Métricas comparativas` (tabla con columnas Variante, Tool, duration_ms_mean, tasa_exito, token_footprint_schema; cada valor con nota al pie referenciando el campo de `metrics.json` o archivo de código del que se extrae), y `## Limitaciones` (las tres limitaciones: startup V2 incluido en latencia, token footprint es estimación estática, LLM mockeado en V3 sin latencia real).

## Verificación

- [ ] Ejecutar `python -c "report = open('outputs/report.md').read(); assert '## Hipótesis evaluadas' in report; assert '## Métricas comparativas' in report; assert '## Limitaciones' in report; assert 'duration_ms' in report or 'latencia' in report; assert 'V2' in report or 'startup' in report; import json; m = json.load(open('traces/metrics.json')); variants = set(r['variant'] for r in m['results']); assert all(v in report for v in variants); print('OK')"` y confirmar `OK` con código de salida 0.
