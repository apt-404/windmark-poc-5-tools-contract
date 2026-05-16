# Plan — F1.10 Decisión ADR-003

## Enfoque

Se genera `outputs/driver.md` a partir del `report.md` completado. La estructura es: contrato elegido con referencia a métricas, triggers de upgrade a MCP como criterios verificables y riesgos asumidos. Requiere `outputs/report.md` final (F1.9 completada).

## Análisis del reporte y selección de variante

- [ ] Leer `outputs/report.md` e identificar la variante con la combinación más favorable de latencia media, tasa de éxito y token footprint; si hay empate entre dos variantes, formular el argumento de desempate basado en criterios de simplicidad operativa y portabilidad del tech-spec; anotar la variante elegida con referencias exactas a las secciones de `report.md`.

## Redacción de driver.md

- [ ] Crear `outputs/driver.md` con las cuatro secciones: `## Contrato elegido` (variante y justificación en 2-4 frases con referencia a sección de `report.md`), `## Evidencia` (tabla de las tres métricas para la variante elegida con referencia al campo de `metrics.json`), `## Triggers de upgrade a MCP` (los tres criterios verificables con definición exacta de qué los activa: segundo cliente independiente, blast radius de la tool, demanda explícita de protocolo MCP), y `## Riesgos asumidos` (derivados de las limitaciones del tech-spec).

## Verificación

- [ ] Ejecutar `python -c "d = open('outputs/driver.md').read(); assert '## Contrato elegido' in d; assert '## Evidencia' in d; assert '## Triggers de upgrade a MCP' in d; assert '## Riesgos asumidos' in d; assert 'report.md' in d or 'metrics.json' in d; print('OK')"` y confirmar `OK` con código de salida 0.
- [ ] Ejecutar `python compare.py --check` y confirmar código de salida 0; ejecutar `python -c "import json; m = json.load(open('traces/metrics.json')); variants = set(r['variant'] for r in m['results']); assert len(variants) >= 2; print('OK')"` y confirmar que hay métricas de al menos dos variantes distintas.
