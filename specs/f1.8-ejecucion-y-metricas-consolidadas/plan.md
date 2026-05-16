# Plan — F1.8 Ejecución y métricas consolidadas

## Enfoque

Se añade soporte de repeticiones al runner para ejecutar N invocaciones por tool y variante. La ejecución real se lanza contra un target HTB Starting Point activo; se asume que `TARGET_IP` está definida en el entorno y hay conectividad (prerequisito de infraestructura externo al agente). El script de ejecución y los parámetros se documentan en `tech-spec.md`. Las trazas se commitean en el repositorio.

## Soporte de repeticiones en compare.py

- [x] Añadir el argumento `--repeat N` (int, default `1`) a `compare.py`, modificar el flujo principal para iterar `repeat` veces por cada combinación (variante, tool) escribiendo una línea JSONL por iteración, y actualizar `consolidate_metrics` para incluir en `metrics.json` los campos `repeat`, `duration_ms_mean` y `duration_ms_values` por (variante, tool) cuando `repeat > 1`.

## Ejecución real (integración)

- [ ] Ejecutar `docker run -e TARGET_IP=$TARGET_IP windmark-poc5 python compare.py --check` y confirmar código de salida 0; a continuación ejecutar el run completo: `docker run -e TARGET_IP=$TARGET_IP -e WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt -v $(pwd)/traces:/app/traces windmark-poc5 python compare.py --target $TARGET_IP --variant all --tool all --repeat 3` y confirmar código de salida 0.

## Tests

- [x] Crear `tests/test_compare_repeat.py` con dos funciones pytest derivadas de los Criterios de Aceptación de `requirements.md`: `test_repeat_argument_iterates_n_times(tmp_path)` usa `unittest.mock.patch` para interceptar las funciones de invocación de variantes y llama al flujo `main()` con `--repeat 2 --variant v1 --tool nmap_scan --target 127.0.0.1 --output str(tmp_path)`, verificando que la función de invocación se llamó exactamente 2 veces; `test_metrics_contains_mean_when_repeat_gt_1(tmp_path)` llama a `consolidate_metrics` con una lista de resultados simulados con `repeat=2` y verifica que `metrics.json` incluye el campo `duration_ms_mean` en al menos una entrada.
- [ ] Ejecutar `pytest tests/test_compare_repeat.py -v` y confirmar exit code 0.

## Documentación y commit de trazas

- [ ] Añadir en la sección `### Desarrollo local` de `tech-spec.md` el comando exacto del run real con los parámetros de 3 repeticiones, el montaje del volumen de traces y las variables de entorno requeridas (`TARGET_IP`, `WORDLIST_PATH`), con nota de que `TARGET_IP` debe estar definida antes de lanzar el contenedor; ejecutar `git add traces/ tech-spec.md` y commitear con mensaje `data(F1.8): metricas run real HTB`.
