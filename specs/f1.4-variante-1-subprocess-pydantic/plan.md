# Plan — F1.4 Variante 1: subprocess + Pydantic

## Enfoque

Se implementan dos funciones puras en `variant-1-subprocess/`, una por tool, que aceptan el modelo de input de `shared/models.py`, invocan el binario con `subprocess.run()` con timeout de 30 s, parsean el output con regex mínimo y devuelven un `ToolResult` con los datos estructurados en `extra`. El JSON schema para tool-use se obtiene directamente con `model_json_schema()` sin ninguna capa adicional.

## Setup del módulo

- [ ] Crear el directorio `variant-1-subprocess/` en la raíz del proyecto.
- [ ] Crear `variant-1-subprocess/__init__.py` vacío para que sea importable como paquete.

## Implementación de nmap_scan

- [ ] Crear `variant-1-subprocess/nmap_scan.py` con la función `run(input: NmapScanInput) -> ToolResult` que importa `NmapScanInput` y `ToolResult` de `shared.models`.
- [ ] Construir el comando nmap: `["nmap"] + input.flags + ["-p", input.ports, input.target]` y ejecutarlo con `subprocess.run(..., capture_output=True, text=True, timeout=30)`.
- [ ] Capturar `stdout` como `raw_output`; si `returncode != 0`, asignar `stderr` o un mensaje descriptivo a `ToolResult.error`.
- [ ] Parsear `raw_output` con regex para extraer `open_ports` (líneas que coincidan con `r"(\d+)/tcp\s+open\s+(\S+)"`) y `service_fingerprints` (tercer grupo si existe).
- [ ] Asignar `extra = {"open_ports": [...], "service_fingerprints": [...]}` en `ToolResult`.
- [ ] Capturar `subprocess.TimeoutExpired` y asignar `ToolResult.error = "timeout"`.

## Implementación de gobuster_dir

- [ ] Crear `variant-1-subprocess/gobuster_dir.py` con la función `run(input: GobusterDirInput) -> ToolResult` que importa `GobusterDirInput` y `ToolResult` de `shared.models`.
- [ ] Construir el comando gobuster: `["gobuster", "dir", "-u", input.target, "-w", input.wordlist]` y añadir `-x`, `",".join(input.extensions)` si `input.extensions` no está vacío; ejecutar con `subprocess.run(..., capture_output=True, text=True, timeout=30)`.
- [ ] Capturar `stdout` como `raw_output`; si `returncode != 0`, asignar el error en `ToolResult.error`.
- [ ] Parsear `raw_output` con regex para extraer `found_paths` y `status_codes`: buscar líneas con `r"(/\S+)\s+\(Status:\s+(\d+)\)"`.
- [ ] Asignar `extra = {"found_paths": [...], "status_codes": {path: code, ...}}` en `ToolResult`.
- [ ] Capturar `subprocess.TimeoutExpired` y asignar `ToolResult.error = "timeout"`.

## Verificación

- [ ] Desde el contenedor Docker, ejecutar `python -c "from variant_1_subprocess.nmap_scan import run; from shared.models import NmapScanInput; r = run(NmapScanInput(target='127.0.0.1')); print(r.exit_code, r.error)"` y verificar que devuelve un `ToolResult` sin excepción (aunque el scan no encuentre puertos abiertos).
- [ ] Ejecutar lo mismo con `gobuster_dir` usando un wordlist accesible y `target='http://127.0.0.1'`; verificar que devuelve `ToolResult` sin excepción.
- [ ] Verificar que `NmapScanInput.model_json_schema()` devuelve un dict con `properties.target`, `properties.ports` y `properties.flags`.
