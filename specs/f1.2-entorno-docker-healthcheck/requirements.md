# F1.2 — Entorno Docker + healthcheck

## Contexto

El runner y las tres variantes corren dentro de un contenedor Docker que incluye Python 3.12, uv, nmap y gobuster. Esta feature crea la imagen base y el sistema de verificación de entorno (`compare.py --check`) que garantiza que todas las dependencias están disponibles antes de ejecutar la comparación.

## Criterios de aceptación

- [ ] `Dockerfile` construye una imagen desde `python:3.12-slim` con nmap y gobuster instalados vía apt.
- [ ] La imagen incluye uv instalado y ejecuta `uv sync --frozen` durante el build a partir de `pyproject.toml` y `uv.lock`.
- [ ] `docker build -t windmark-poc5 .` completa sin errores.
- [ ] `docker run windmark-poc5 nmap --version` devuelve la versión de nmap sin errores.
- [ ] `docker run windmark-poc5 gobuster --version` devuelve la versión de gobuster sin errores.
- [ ] `compare.py --check` verifica en orden: nmap en PATH, gobuster en PATH, wordlist accesible (`WORDLIST_PATH`), al menos un fixture presente en `traces/fixtures/`.
- [ ] Si `TARGET_IP` está definida, `compare.py --check` añade verificación de conectividad con ping; si no está definida, el check pasa sin verificar red.
- [ ] `compare.py --check` imprime una tabla de estado por dependencia (OK / ERROR) y devuelve código de salida 0 si todo OK, 1 si alguna dependencia falla.

## Fuera de alcance

- Docker Compose (sin orquestación multi-contenedor en esta PoC).
- Imagen base Kali (elegida python:3.12-slim + apt).
- Variables de entorno adicionales a `TARGET_IP`, `WORDLIST_PATH`, `MCP_SERVER_TIMEOUT`.
- Wordlist incluida en la imagen (se monta como volumen o se usa la ruta por defecto si existe en el contenedor).

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| — | — | — |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Imagen base | `python:3.12-slim` + nmap/gobuster vía apt | `kalilinux/kali-rolling` |
| Gestión de dependencias Python | `uv sync --frozen` desde `pyproject.toml` en el build | `pip install -r requirements.txt` |
| Healthcheck de red | Ping al target si `TARGET_IP` definida (opcional) | Sin verificación de conectividad |
