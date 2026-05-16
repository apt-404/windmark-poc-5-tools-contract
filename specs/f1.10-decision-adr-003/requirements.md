# F1.10 — Decisión ADR-003

## Contexto

`outputs/driver.md` cierra ADR-003 documentando el contrato de invocación de tools elegido para el MVP de Windmark AI con evidencia trazable a `outputs/report.md`. También cierra los tres triggers de upgrade a MCP como criterios verificables, que es el último requisito del Gate Final de la PoC.

## Criterios de aceptación

- [ ] `outputs/driver.md` declara el contrato elegido (V1, V2 o V3) con referencia explícita a la sección y métrica concreta de `outputs/report.md` que respalda la decisión.
- [ ] Si hay empate sin ganador claro en las métricas, la decisión se documenta con justificación explícita y argumento que no sea tautológico.
- [ ] `outputs/driver.md` cierra los tres triggers de upgrade a MCP como criterios verificables:
  - **Segundo cliente**: definición concreta de qué cuenta como segundo cliente del catálogo de tools (p.ej. un segundo agente Python con imports distintos, un servicio externo que consuma las tools por HTTP).
  - **Blast radius**: umbral concreto que justifica un contenedor separado (p.ej. una tool con acceso a filesystem, una tool que crea procesos con privilegios elevados).
  - **Demanda comercial**: condición verificable que obliga a MCP (p.ej. un cliente externo que requiera integrar las tools vía protocolo MCP estándar).
- [ ] `outputs/driver.md` documenta los riesgos asumidos con el contrato elegido.
- [ ] `outputs/driver.md` no contiene afirmaciones sin referencia a datos del `report.md` o a decisiones explícitas del proceso.

## Fuera de alcance

- Alternativas descartadas con justificación extendida (se infieren de `report.md`).
- Rediseño del contrato de datos (ADR-002 ya está cerrado).
- Decisiones de integración con el orquestador del MVP (responsabilidad de ADR-002 de PoC #4).

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.9 — Reporte comparativo | Feature interna | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Triggers de upgrade a MCP | Criterios verificables y concretos (requisito Gate Final) | Descripción cualitativa como en el KB |
| Alternativas descartadas en driver.md | No incluidas (se infieren de report.md) | Tabla de alternativas con evidencia por variante |
