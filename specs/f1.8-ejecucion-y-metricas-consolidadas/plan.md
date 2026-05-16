# Plan — F1.8 Ejecución y métricas consolidadas

## Enfoque

Se añade soporte de repeticiones al runner para ejecutar N invocaciones por tool y variante. La ejecución real se lanza contra un target HTB Starting Point activo; se asume que `TARGET_IP` está definida en el entorno y hay conectividad (prerequisito de infraestructura externo al agente). El script de ejecución y los parámetros se documentan en `tech-spec.md`. Las trazas se commitean en el repositorio.

## Soporte de repeticiones en compare.py

- [ ] Añadir el argumento `--repeat N` (int, default `1`) a `compare.py`, modificar el flujo principal para iterar `repeat` veces por cada combinación (variante, tool) escribiendo una línea JSONL por iteración, y actualizar `consolidate_metrics` para incluir en `metrics.json` los campos `repeat`, `duration_ms_mean` y `duration_ms_values` por (variante, tool) cuando `repeat > 1`.

## Verificación de entorno y ejecución del run real

- [ ] Ejecutar `docker run -e TARGET_IP=$TARGET_IP windmark-poc5 python compare.py --check` y confirmar código de salida 0; a continuación ejecutar el run completo: `docker run -e TARGET_IP=$TARGET_IP -e WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt -v $(pwd)/traces:/app/traces windmark-poc5 python compare.py --target $TARGET_IP --variant all --tool all --repeat 3` y confirmar código de salida 0.
- [ ] Verificar con `python -c "import json; m = json.load(open('traces/metrics.json')); assert m['total_invocations'] >= 6, f'solo {m[\"total_invocations\"]} invocaciones'; assert any('duration_ms_mean' in str(r) for r in m['results']); print('OK')"` que `metrics.json` contiene al menos 6 invocaciones y los campos de media.

## Documentación y commit de trazas

- [ ] Añadir en la sección `### Desarrollo local` de `tech-spec.md` el comando exacto del run real con los parámetros de 3 repeticiones, el montaje del volumen de traces y las variables de entorno requeridas (`TARGET_IP`, `WORDLIST_PATH`), con nota de que `TARGET_IP` debe estar definida antes de lanzar el contenedor; ejecutar `git add traces/ tech-spec.md` y commitear con mensaje `data(F1.8): metricas run real HTB`.
