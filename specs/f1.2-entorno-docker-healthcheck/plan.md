# Plan — F1.2 Entorno Docker + healthcheck

## Enfoque

Se crea el `Dockerfile` sobre `python:3.12-slim` instalando uv, nmap y gobuster. El `pyproject.toml` define las dependencias de runtime y el build ejecuta `uv sync --frozen`. El subcomando `--check` de `compare.py` actúa como healthcheck ejecutable: verifica binarios, archivos y opcionalmente conectividad de red si `TARGET_IP` está definida.

## Setup de pyproject.toml

- [ ] Crear `pyproject.toml` en la raíz con `[project]` (nombre `windmark-poc5`, requires-python `>=3.12`) y sección `[project.dependencies]` con `pydantic>=2.0`, `fastmcp`, `litellm`, `structlog`.
- [ ] Ejecutar `uv lock` en el host para generar `uv.lock` antes del primer build Docker.

## Dockerfile

- [ ] Crear `Dockerfile` con `FROM python:3.12-slim` y `WORKDIR /app`.
- [ ] Añadir capa de sistema: `RUN apt-get update && apt-get install -y --no-install-recommends nmap gobuster iputils-ping && rm -rf /var/lib/apt/lists/*`.
- [ ] Añadir instalación de uv: `RUN pip install uv --no-cache-dir`.
- [ ] Añadir copia de lockfiles y sync: `COPY pyproject.toml uv.lock ./` seguido de `RUN uv sync --frozen --no-dev`.
- [ ] Añadir copia del código fuente: `COPY . .`.
- [ ] Añadir variables de entorno default: `ENV WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt` y `ENV MCP_SERVER_TIMEOUT=10`.

## Implementación de --check en compare.py

- [ ] Crear `compare.py` en la raíz con el argumento `--check` (stub inicial; el runner completo se implementa en F1.7).
- [ ] Implementar verificación de `nmap` con `shutil.which("nmap")`; registrar OK o ERROR en la tabla de estado.
- [ ] Implementar verificación de `gobuster` con `shutil.which("gobuster")`; registrar OK o ERROR.
- [ ] Implementar verificación del wordlist: comprobar que el archivo en `os.environ.get("WORDLIST_PATH")` existe y es legible con `os.path.isfile()`; registrar OK o ERROR.
- [ ] Implementar verificación de fixtures: comprobar que `traces/fixtures/` existe y contiene al menos un archivo `.json` con `glob.glob("traces/fixtures/*.json")`; registrar OK o ERROR.
- [ ] Implementar verificación de red opcional: si `TARGET_IP` está en el entorno, ejecutar `subprocess.run(["ping", "-c", "1", "-W", "2", target_ip])` y registrar OK o ERROR según el código de salida.
- [ ] Imprimir la tabla de estado (columnas: Dependencia, Estado) y salir con `sys.exit(0)` si todo OK, `sys.exit(1)` si alguna falla.

## Verificación

- [ ] Ejecutar `docker build -t windmark-poc5 .` y confirmar que completa sin errores.
- [ ] Ejecutar `docker run windmark-poc5 nmap --version` y `docker run windmark-poc5 gobuster --version`; verificar que ambos devuelven versión.
- [ ] Ejecutar `docker run windmark-poc5 python compare.py --check` sin `TARGET_IP` y verificar que la tabla muestra nmap, gobuster, wordlist y fixtures con su estado, y que el código de salida es el correcto.
