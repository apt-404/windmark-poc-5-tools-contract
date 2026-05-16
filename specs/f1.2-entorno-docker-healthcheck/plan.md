# Plan — F1.2 Entorno Docker + healthcheck

## Enfoque

Se crea el `Dockerfile` sobre `python:3.12-slim` instalando uv, nmap y gobuster. El `pyproject.toml` define las dependencias de runtime y el build ejecuta `uv sync --frozen`. El subcomando `--check` de `compare.py` actúa como healthcheck ejecutable: verifica binarios, archivos y opcionalmente conectividad de red si `TARGET_IP` está definida.

## Configuración de dependencias

- [ ] Crear `pyproject.toml` en la raíz con sección `[project]` (nombre `windmark-poc5`, requires-python `>=3.12`) y sección `[project.dependencies]` con `pydantic>=2.0`, `fastmcp`, `litellm`, `structlog`; ejecutar `uv lock` para generar `uv.lock`.

## Dockerfile

- [ ] Crear `Dockerfile` completo con `FROM python:3.12-slim`, `WORKDIR /app`, capa de sistema (`apt-get install -y --no-install-recommends nmap gobuster iputils-ping`), instalación de uv (`pip install uv --no-cache-dir`), copia de lockfiles y sync (`COPY pyproject.toml uv.lock ./` + `RUN uv sync --frozen --no-dev`), copia del código fuente (`COPY . .`), y variables de entorno `ENV WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt` y `ENV MCP_SERVER_TIMEOUT=10`.

## Subcomando --check en compare.py

- [ ] Crear `compare.py` en la raíz con argumento `--check` usando `argparse` e implementar la verificación completa: `nmap` y `gobuster` con `shutil.which()`, wordlist con `os.path.isfile()`, fixtures con `glob.glob("traces/fixtures/*.json")`, y ping a `TARGET_IP` si está en el entorno con `subprocess.run(["ping", "-c", "1", "-W", "2", target_ip])`; imprimir tabla de estado (Dependencia | Estado) y salir con `sys.exit(0)` si todo OK o `sys.exit(1)` si alguna falla.

## Verificación

- [ ] Ejecutar `docker build -t windmark-poc5 .` y confirmar código de salida 0; ejecutar `docker run windmark-poc5 nmap --version` y `docker run windmark-poc5 gobuster --version` y confirmar que ambos devuelven versión con código de salida 0.
- [ ] Ejecutar `docker run windmark-poc5 python compare.py --check` sin `TARGET_IP` y confirmar que el código de salida es 1 (fallan fixtures al no existir aún) y que stdout contiene las líneas `nmap`, `gobuster` y `wordlist`.
