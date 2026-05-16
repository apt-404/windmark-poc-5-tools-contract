# Plan — F1.8 Ejecución y métricas consolidadas

## Enfoque

Se añade soporte de repeticiones al runner para ejecutar N invocaciones por tool y variante, se conecta la VPN HTB y se levanta una máquina Starting Point como target real. El run produce los JSONL por invocación y `traces/metrics.json` consolidado. El script de ejecución se documenta en `tech-spec.md` para reproducibilidad.

## Soporte de repeticiones en compare.py

- [ ] Añadir el argumento `--repeat N` (int, default `1`) a `compare.py` que ejecuta N invocaciones por tool y variante en el mismo run.
- [ ] Modificar el flujo principal para iterar `repeat` veces por cada combinación (variante, tool) y escribir una línea JSONL por iteración.
- [ ] Actualizar `consolidate_metrics` para incluir en `metrics.json` el campo `repeat` y calcular `duration_ms_mean` y `duration_ms_values` por (variante, tool) cuando `repeat > 1`.

## Preparación del entorno HTB

- [ ] Conectar la VPN HTB con `openvpn <lab.ovpn>` en el host (fuera del contenedor).
- [ ] Levantar una máquina HTB Starting Point y anotar la IP asignada.
- [ ] Verificar conectividad: `ping -c 3 <TARGET_IP>` desde el host.
- [ ] Ejecutar el healthcheck en el contenedor: `docker run -e TARGET_IP=<IP> windmark-poc5 python compare.py --check` y confirmar código de salida 0.

## Ejecución del run real

- [ ] Ejecutar el run completo con 3 repeticiones: `docker run -e TARGET_IP=<IP> -e WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt -v $(pwd)/traces:/app/traces windmark-poc5 python compare.py --target <IP> --variant all --tool all --repeat 3`.
- [ ] Verificar que el proceso termina con código de salida 0.
- [ ] Verificar que `traces/metrics.json` contiene al menos 12 invocaciones (si las 3 variantes completan) o más de 0 (tolerancia a fallos de V2).

## Documentación del script en tech-spec.md

- [ ] Añadir en la sección `### Desarrollo local` de `tech-spec.md` el comando exacto del run real con los parámetros de 3 repeticiones, incluyendo el montaje del volumen de traces y las variables de entorno requeridas.
- [ ] Añadir nota sobre la VPN HTB: que debe estar activa antes de lanzar el contenedor.

## Commit de trazas

- [ ] Añadir `traces/metrics.json` y los JSONL de `traces/v1/`, `traces/v2/`, `traces/v3/` al repositorio con `git add traces/` y commitear con mensaje `data(F1.8): metricas run real HTB`.
- [ ] Verificar que `traces/fixtures/` ya está presente (de F1.3) y no se sobreescribe.
