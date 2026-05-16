# F1.8 — Ejecución y métricas consolidadas

## Contexto

Con las tres variantes funcionales y el runner operativo, esta feature cubre la ejecución real de la comparación contra el target Tier 0 (máquina HTB Starting Point) y la obtención de `traces/metrics.json` con datos por invocación suficientes para redactar el `report.md`. Se documentan los comandos exactos en `tech-spec.md` para que el run sea reproducible.

## Criterios de aceptación

- [ ] `compare.py --check` devuelve código de salida 0 en el contenedor Docker antes de iniciar el run (nmap, gobuster, wordlist, fixtures disponibles; target alcanzable con ping).
- [ ] El run completo ejecuta 3 invocaciones por tool y variante (18 invocaciones totales: 3 variantes × 2 tools × 3 repeticiones).
- [ ] `traces/metrics.json` existe y contiene las 18 invocaciones (o menos si alguna variante falló) con los campos `variant`, `tool`, `duration_ms`, `exit_code`, `error` por invocación.
- [ ] Al menos dos variantes completan sin error (`error is None`) para que el runner devuelva código de salida 0.
- [ ] Los JSONL individuales existen en `traces/<variant>/<tool>/` con una línea por invocación.
- [ ] El script de ejecución (docker run con los parámetros del run real) está documentado en `tech-spec.md` en la sección de Deployment.
- [ ] `traces/` y `traces/metrics.json` están commitados en el repositorio.

## Fuera de alcance

- Análisis o interpretación de las métricas (pertenece a F1.9).
- Automatización del run como CI/CD.
- Más de 3 repeticiones por tool y variante.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| F1.7 — Runner de comparación | Feature interna | Pendiente |
| Máquina HTB Starting Point | Servicio externo | Pendiente |
| VPN HTB | Servicio externo | Pendiente |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Target Tier 0 | Máquina HTB Starting Point (con VPN) | Stub local (contenedor con nginx) |
| Invocaciones por tool/variante | 3 repeticiones (18 invocaciones totales) | 1 repetición (6 invocaciones totales) |
| Reproducibilidad | Script shell documentado en `tech-spec.md` | Ejecución manual sin documentar |
