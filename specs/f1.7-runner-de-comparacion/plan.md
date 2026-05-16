# Plan — F1.7 Runner de comparación

## Enfoque

Se completa `compare.py` (iniciado en F1.2 con el subcomando `--check`) añadiendo el flujo principal de comparación. El runner invoca V1 y V3 como imports directos y V2 arrancando el proceso FastMCP por stdio. Por cada invocación escribe una línea JSONL en `traces/` y al terminar consolida `metrics.json`. Los fallos de variante se capturan en `ToolResult.error` sin interrumpir el flujo.

## CLI, logging y métricas

- [ ] Añadir a `compare.py` los argumentos `--target` (str), `--variant` (str, default `all`, validado contra `v1|v2|v3|all`), `--tool` (str, default `all`, validado contra `nmap_scan|gobuster_dir|all`) y `--output` (str, default `traces/`); implementar `write_jsonl(result, variant, tool, output_dir)` que crea `output_dir/<variant>/<tool>/` si no existe y escribe una línea JSONL con timestamp ISO-8601, `variant`, `tool`, `duration_ms`, `exit_code`, `error` y `output_summary` (primeros 200 chars de `raw_output`); implementar `consolidate_metrics(results, output_dir)` que escribe `output_dir/metrics.json` con `total_invocations`, `variants_ok`, `variants_error` y `results`.

## Funciones de invocación V1 y V3

- [ ] Implementar `run_v1(target, tool, output_dir) -> ToolResult` que importa `run()` del módulo V1 correspondiente y mide `duration_ms` con `time.perf_counter()`; implementar `run_v3(target, tool, fixture_dir, output_dir) -> ToolResult` que importa `run_nmap` o `run_gobuster` de V3 con la ruta de fixture correspondiente.

## Función de invocación V2 (MCP)

- [ ] Implementar `run_v2(target, tool, output_dir, timeout_s) -> ToolResult` que arranca el proceso FastMCP con `start_mcp_server()`, espera confirmación con `wait_for_mcp_ready()`, envía la invocación JSON-RPC para la tool solicitada y captura la respuesta; si el server no arranca en `timeout_s`, devuelve `ToolResult` con `error="mcp_server_timeout"`.

## Flujo principal

- [ ] Implementar el flujo `main()` que selecciona variantes y tools según los argumentos, invoca en orden secuencial V1, V2, V3 para cada tool, llama a `write_jsonl` tras cada invocación, captura cualquier excepción no esperada y la convierte en `ToolResult.error`, llama a `consolidate_metrics` y sale con código 0 si al menos un resultado tiene `error is None`, código 1 si todos tienen error.

## Verificación

- [ ] Ejecutar `docker run windmark-poc5 python compare.py --target 127.0.0.1 --variant v1 --tool nmap_scan` y verificar con `python -c "import glob, json; files = glob.glob('traces/v1/nmap_scan/*.jsonl'); assert files; row = json.loads(open(files[0]).readline()); assert 'exit_code' in row and 'duration_ms' in row and 'variant' in row; print('OK')"` que el JSONL existe con los campos correctos.
- [ ] Ejecutar `python compare.py --variant all --tool all --target 127.0.0.1` y verificar con `python -c "import json; m = json.load(open('traces/metrics.json')); assert m['total_invocations'] > 0 and 'results' in m and 'variants_ok' in m; print('OK')"` que `metrics.json` es válido.
- [ ] Ejecutar `python compare.py --variant v2 --tool nmap_scan --target 127.0.0.1` con el servidor MCP inaccesible y confirmar con `python -c "import json; m = json.load(open('traces/metrics.json')); errs = [r for r in m['results'] if r.get('variant') == 'v2' and r.get('error')]; assert errs; print('OK')"` que el error queda registrado en `metrics.json`.
