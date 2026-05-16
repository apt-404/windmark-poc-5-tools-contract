# F1.7 — Runner de comparación

## Contexto

`compare.py` es el punto de entrada del experimento. Invoca las tres variantes secuencialmente sobre el mismo target con los mismos inputs, mide el tiempo de ejecución por invocación, escribe JSONL por invocación en `traces/` y consolida `traces/metrics.json` al terminar. No contiene lógica de tools ni de agente.

## Criterios de aceptación

- [ ] `compare.py` acepta los argumentos CLI: `--target` (required), `--variant` (default `all`; acepta `v1`, `v2`, `v3`, `all`), `--tool` (default `all`; acepta `nmap_scan`, `gobuster_dir`, `all`), `--output` (default `traces/`).
- [ ] El runner invoca las variantes en orden secuencial: V1, V2, V3.
- [ ] Por cada invocación de tool, el runner escribe una línea JSONL en `traces/<variant>/<tool>/<timestamp>.jsonl` con los campos: `variant`, `tool`, `input_params`, `duration_ms`, `exit_code`, `error`, `output_summary`.
- [ ] Al terminar todas las invocaciones, el runner consolida `traces/metrics.json` con todos los resultados y los campos: `total_invocations`, `variants_ok`, `variants_error`, `results` (lista de todas las invocaciones).
- [ ] Si una variante falla completamente (p.ej. el servidor MCP no arranca), el runner la registra como error en JSONL y continúa con las siguientes sin lanzar excepción.
- [ ] El proceso termina con código de salida 0 si al menos una variante completó sin error; con código 1 si todas fallaron.
- [ ] El runner no contiene lógica de tools: no ejecuta subprocess de nmap ni gobuster directamente; solo llama a las funciones `run()` de cada variante y al servidor MCP de V2.

## Fuera de alcance

- Ejecución paralela de variantes (secuencial en esta PoC).
- Retry ante fallos de tool o de variante.
- Visualización o análisis de resultados (eso pertenece a F1.9).
- Integración con un LLM real.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.4 — Variante 1: subprocess + Pydantic | Feature interna | Pendiente |
| F1.5 — Variante 2: MCP server stdio | Feature interna | Pendiente |
| F1.6 — Variante 3: tool-use nativo | Feature interna | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Orden de ejecución | Secuencial (V1 → V2 → V3) | Paralela con threading/asyncio |
| Logging | JSONL por invocación + `metrics.json` consolidado al final | Solo `metrics.json` al final |
| Tolerancia a fallos | Continúa con las otras variantes y reporta el fallo | Para al primer fallo |
