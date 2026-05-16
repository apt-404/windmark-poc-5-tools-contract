# Plan — F1.10 Decisión ADR-003

## Enfoque

Se genera `outputs/driver.md` a partir del `report.md` completado. La estructura es: contrato elegido con referencia a métricas, triggers de upgrade a MCP como criterios verificables y riesgos asumidos. Requiere `outputs/report.md` final (F1.9 completada).

## Análisis del reporte y selección de variante

- [x] Leer `outputs/report.md` e identificar la variante con la combinación más favorable de latencia media, tasa de éxito y token footprint; si hay empate entre dos variantes, formular el argumento de desempate basado en criterios de simplicidad operativa y portabilidad del tech-spec; anotar la variante elegida con referencias exactas a las secciones de `report.md`.

## Redacción de driver.md

- [ ] Crear `outputs/driver.md` con las cuatro secciones: `## Contrato elegido` (variante y justificación en 2-4 frases con referencia a sección de `report.md`), `## Evidencia` (tabla de las tres métricas para la variante elegida con referencia al campo de `metrics.json`), `## Triggers de upgrade a MCP` (los tres criterios verificables con definición exacta de qué los activa: segundo cliente independiente, blast radius de la tool, demanda explícita de protocolo MCP), y `## Riesgos asumidos` (derivados de las limitaciones del tech-spec).

## Tests

- [ ] Crear `tests/test_adr_driver.py` con dos funciones pytest derivadas de los Criterios de Aceptación de `requirements.md`: `test_driver_contains_required_sections()` lee `outputs/driver.md` y verifica que contiene las secciones `## Contrato elegido`, `## Evidencia`, `## Triggers de upgrade a MCP` y `## Riesgos asumidos`; `test_driver_references_evidence_source()` verifica que `outputs/driver.md` contiene al menos una referencia a `report.md` o `metrics.json` como fuente de evidencia trazable.
- [ ] Ejecutar `pytest tests/test_adr_driver.py -v` y confirmar exit code 0.
