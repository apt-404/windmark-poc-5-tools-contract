# Plan — F1.4 Variante 1: subprocess + Pydantic

## Enfoque

Se implementan dos funciones puras en `variant-1-subprocess/`, una por tool, que aceptan el modelo de input de `shared/models.py`, invocan el binario con `subprocess.run()` con timeout de 30 s, parsean el output con regex mínimo y devuelven un `ToolResult` con los datos estructurados en `extra`. El JSON schema para tool-use se obtiene directamente con `model_json_schema()` sin ninguna capa adicional.

## Módulo nmap_scan

- [ ] Crear el directorio `variant-1-subprocess/` con `__init__.py` vacío y `nmap_scan.py` con la función `run(input: NmapScanInput) -> ToolResult` completa: construir el comando `["nmap"] + input.flags + ["-p", input.ports, input.target]`, ejecutar con `subprocess.run(..., capture_output=True, text=True, timeout=30)`, parsear `stdout` con regex `r"(\d+)/tcp\s+open\s+(\S+)"` para extraer `open_ports` y `service_fingerprints`, asignar `extra` y capturar `TimeoutExpired` con `error="timeout"`.

## Módulo gobuster_dir

- [ ] Crear `variant-1-subprocess/gobuster_dir.py` con la función `run(input: GobusterDirInput) -> ToolResult` completa: construir el comando gobuster añadiendo `-x` y `",".join(input.extensions)` si `extensions` no está vacío, ejecutar con `subprocess.run()` con timeout 30 s, parsear `stdout` con regex `r"(/\S+)\s+\(Status:\s+(\d+)\)"` para extraer `found_paths` y `status_codes`, asignar `extra` y capturar `TimeoutExpired`.

## Verificación

- [ ] Desde el contenedor Docker, ejecutar `python -c "from variant_1_subprocess.nmap_scan import run as run_nmap; from variant_1_subprocess.gobuster_dir import run as run_gobuster; from shared.models import NmapScanInput, GobusterDirInput; r1 = run_nmap(NmapScanInput(target='127.0.0.1')); assert r1.exit_code is not None and isinstance(r1.extra, dict); r2 = run_gobuster(GobusterDirInput(target='http://127.0.0.1', wordlist='/usr/share/wordlists/dirb/common.txt')); assert r2.exit_code is not None; s = NmapScanInput.model_json_schema(); assert 'target' in s['properties'] and 'ports' in s['properties']; print('OK')"` y confirmar `OK` con código de salida 0.
