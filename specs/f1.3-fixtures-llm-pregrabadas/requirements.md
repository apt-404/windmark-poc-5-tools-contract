# F1.3 — Fixtures LLM pregrabadas

## Contexto

La variante V3 simula el ciclo de tool-use del LLM sin hacer llamadas reales a la API. Las fixtures son archivos JSON estáticos con `function_call` blocks en formato OpenAI que V3 lee como si fueran la respuesta del LLM, extrae los parámetros y ejecuta el binario. Se graban una sola vez con ayuda del claude CLI y se mantienen como archivos estáticos en el repositorio.

## Criterios de aceptación

- [ ] Existe `traces/fixtures/nmap_scan.json` con un `function_call` block en formato OpenAI que incluye los parámetros `target`, `ports` y `flags`.
- [ ] Existe `traces/fixtures/gobuster_dir.json` con un `function_call` block en formato OpenAI que incluye los parámetros `target`, `wordlist` y `extensions`.
- [ ] Los campos de cada fixture son: `id`, `type: "function"`, `function.name` y `function.arguments` (string JSON con los parámetros de la tool).
- [ ] `json.loads(fixture["function"]["arguments"])` extrae un dict válido con los parámetros de la tool sin errores.
- [ ] Las dos fixtures están commitadas en el repositorio bajo `traces/fixtures/`.
- [ ] `compare.py --check` detecta las fixtures como presentes y devuelve OK para ese check.

## Fuera de alcance

- Múltiples fixtures por tool (una por tool es suficiente para verificar el contrato de V3).
- Fixtures en formato Anthropic nativo (`tool_use` blocks).
- Generación automática de fixtures en tiempo de ejecución del runner.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| claude CLI | Herramienta externa | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Número de fixtures por tool | Una por tool (`nmap_scan.json`, `gobuster_dir.json`) | Múltiples fixtures por tool |
| Método de generación | claude CLI como referencia; fixture final escrita en formato OpenAI | Fixture escrita a mano sin referencia del CLI |
| Formato de fixture | OpenAI `function_call` (`id`, `type`, `function.name`, `function.arguments`) | Anthropic `tool_use` block nativo |
