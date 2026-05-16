# Plan — F1.7 Runner de comparación

## Enfoque

Se completa `compare.py` (iniciado en F1.2 con el subcomando `--check`) añadiendo el flujo principal de comparación. El runner invoca V1 y V3 como imports directos y V2 arrancando el proceso FastMCP por stdio. Por cada invocación escribe una línea JSONL en `traces/` y al terminar consolida `metrics.json`. Los fallos de variante se capturan en `ToolResult.error` sin interrumpir el flujo.

## Argumentos CLI

- [ ] Añadir a `compare.py` los argumentos `--target` (str, required cuando no se usa `--check`), `--variant` (str, default `all`), `--tool` (str, default `all`) y `--output` (str, default `traces/`) usando `argparse`.
- [ ] Validar que `--variant` sea uno de `v1`, `v2`, `v3`, `all`; si no, imprimir error y salir con código 1.
- [ ] Validar que `--tool` sea uno de `nmap_scan`, `gobuster_dir`, `all`; si no, imprimir error y salir con código 1.

## Lógica de invocación por variante

- [ ] Implementar `run_v1(target, tool, output_dir) -> ToolResult` que importa la función `run()` del módulo de V1 correspondiente, mide `duration_ms` con `time.perf_counter()` y devuelve el `ToolResult`.
- [ ] Implementar `run_v2(target, tool, output_dir, timeout_s) -> ToolResult` que arranca el proceso FastMCP (función `start_mcp_server()` de F1.5), espera el `tools/list` de confirmación, envía la invocación JSON-RPC y captura la respuesta; si el server no arranca en `timeout_s`, devuelve `ToolResult` con `error`.
- [ ] Implementar `run_v3(target, tool, fixture_dir, output_dir) -> ToolResult` que importa `run_nmap` o `run_gobuster` de V3 con la ruta de fixture correspondiente y devuelve el `ToolResult`.

## Logging JSONL por invocación

- [ ] Implementar `write_jsonl(result: ToolResult, variant, tool, output_dir)` que: crea el directorio `output_dir/<variant>/<tool>/` si no existe; escribe una línea JSONL con timestamp ISO-8601 y los campos `variant`, `tool`, `input_params`, `duration_ms`, `exit_code`, `error`, `output_summary` (primeros 200 chars de `raw_output`).

## Consolidación de metrics.json

- [ ] Implementar `consolidate_metrics(results: list[dict], output_dir)` que escribe `output_dir/metrics.json` con los campos: `total_invocations`, `variants_ok` (count con `error is None`), `variants_error` (count con `error is not None`), `results` (lista completa).
- [ ] Llamar a `consolidate_metrics` al terminar todas las invocaciones, antes de salir.

## Flujo principal y código de salida

- [ ] Implementar el flujo principal que: selecciona variantes y tools según `--variant` y `--tool`; invoca en orden secuencial V1, V2, V3 para cada tool; llama a `write_jsonl` tras cada invocación; captura cualquier excepción no esperada y la convierte en `ToolResult.error`; llama a `consolidate_metrics`; sale con código 0 si al menos un resultado tiene `error is None`, código 1 si todos tienen error.

## Verificación

- [ ] Ejecutar `docker run windmark-poc5 python compare.py --target 127.0.0.1 --variant v1 --tool nmap_scan` y verificar que se crea `traces/v1/nmap_scan/<timestamp>.jsonl` con los campos correctos.
- [ ] Ejecutar `python compare.py --variant all --tool all --target 127.0.0.1` y verificar que se crea `traces/metrics.json` con `total_invocations`, `variants_ok`, `variants_error` y `results`.
- [ ] Verificar que si se ejecuta solo `--variant v2` y el servidor no arranca, el código de salida es 1 y `metrics.json` refleja el error.
