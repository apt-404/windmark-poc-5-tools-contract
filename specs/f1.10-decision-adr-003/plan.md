# Plan — F1.10 Decisión ADR-003

## Enfoque

Se redacta `outputs/driver.md` a partir del `report.md` completado. La estructura es: contrato elegido con referencia a métricas, triggers de upgrade a MCP como criterios verificables y riesgos asumidos. No se redacta hasta tener `outputs/report.md` final (F1.9 completada).

## Análisis de report.md para la decisión

- [ ] Leer `outputs/report.md` e identificar qué variante tiene la combinación más favorable de latencia media, tasa de éxito y token footprint de schema.
- [ ] Si una variante domina en las tres métricas, anotarla como candidata con las referencias de sección exactas.
- [ ] Si hay empate entre dos variantes, redactar el argumento de desempate basado en criterios arquitectónicos del tech-spec (simplicidad operativa, portabilidad futura a MCP).

## Redacción de driver.md

- [ ] Crear `outputs/driver.md` con sección `## Contrato elegido` que declare la variante y explique la decisión en 2-4 frases con referencia a la sección de métricas de `report.md`.
- [ ] Añadir sección `## Evidencia` con tabla de las tres métricas (latencia media, tasa de éxito, token footprint) para la variante elegida y referencia al dato en `metrics.json`.
- [ ] Añadir sección `## Triggers de upgrade a MCP` con los tres criterios concretos y verificables:
  - **Segundo cliente**: definir exactamente qué cuenta (p.ej. un segundo proceso Python independiente que necesite invocar las mismas tools, o un servicio externo vía HTTP).
  - **Blast radius**: definir el umbral (p.ej. cualquier tool que ejecute comandos con privilegios elevados o que modifique el sistema de archivos fuera del directorio de trabajo).
  - **Demanda comercial**: definir la condición (p.ej. un cliente o integración que requiera explícitamente protocolo MCP como contrato de integración, no solo Python callable).
- [ ] Añadir sección `## Riesgos asumidos` con los riesgos del contrato elegido derivados de las limitaciones conocidas del tech-spec.

## Verificación de criterios de cierre

- [ ] Verificar que cada afirmación en `## Contrato elegido` tiene referencia a `report.md`.
- [ ] Verificar que los tres triggers de `## Triggers de upgrade a MCP` son verificables: para cada uno, comprobar que existe una pregunta de sí/no que los cierra (p.ej. "¿hay un segundo proceso independiente consumiendo las tools?" → sí/no).
- [ ] Verificar que `compare.py --check` devuelve código 0 (Gate Final, condición 1).
- [ ] Verificar que `traces/metrics.json` contiene métricas de al menos dos variantes con `duration_ms` y `exit_code` (Gate Final, condición 3).
- [ ] Verificar que `outputs/report.md` incluye la tabla comparativa con las tres métricas (Gate Final, condición 4).
- [ ] Verificar que `outputs/driver.md` declara el contrato elegido con referencia explícita a `report.md` (Gate Final, condición 5).
- [ ] Verificar que los tres triggers están documentados como criterios verificables (Gate Final, condición 6).
