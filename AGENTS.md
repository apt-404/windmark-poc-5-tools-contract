# AGENTS.md — Windmark PoC #5: Contrato de Tools

Este fichero lista los documentos del knowledge base que **siempre deben estar presentes** al trabajar en este repositorio. Antes de implementar, revisar o tomar decisiones sobre código, consulta estos specs.

## 📚 Documentos de referencia obligatorios

| Documento | URL | Qué contiene |
|-----------|-----|--------------|
| **Product Spec MVP** | https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/product-spec.md | Visión del MVP, problem statement, principios de diseño, arquitectura objetivo, interfaces CLI (`windmark run`, `score`, `report`, `doctor`), deliverables y out-of-scope |
| **Tech Spec MVP** | https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md | Stack técnico (Python 3.12, uv, Pydantic v2, LiteLLM, SQLite), estructura de módulos, **ADR-001** (VPN namespacing), **ADR-002** (Custom ReAct + LiteLLM), **ADR-003** (subprocess+Pydantic vs MCP — el que decide esta PoC), discovery items abiertos |
| **Roadmap MVP** | https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/roadmap.md | Fase 0 (6 PoCs paralelizables y sus hipótesis), Fase 1 (Tier 0/1/2 features y criterios de cierre), dependency graph, gates Fase 0→1 y MVP→VP |

## 🎯 Foco de esta PoC

Esta PoC decide **ADR-003**: si `subprocess + Pydantic in-process` es suficiente como contrato de invocación de tools para el MVP, o hay que saltar a MCP server local.

Las secciones del Tech Spec más relevantes para el trabajo diario:

- `ADR-003` — decisión provisional que esta PoC debe confirmar o revisar
- `windmark/tools/` — estructura esperada del módulo de tools en el MVP (función pura por tool, Pydantic in/out, `model_json_schema()`)
- `## ❓ Discovery` → ítem *"Contrato definitivo de tools (in-process subprocess vs MCP vs tool-use nativo). Bloqueado por PoC #5."*

Las secciones del Roadmap más relevantes:

- `PoC #5 — Contrato de invocación de tools` — hipótesis, diseño funcional, criterios de éxito y output esperado
- `## 🔗 Dependency Graph` — esta PoC bloquea a PoC #4 (orquestación) y a `F0.5` (catálogo de tools Tier 0)

## ⚠️ Restricciones a recordar

- El output de esta PoC es un **`driver.md`** con decisión trazable. No basta con que el código funcione: la conclusión decisional debe estar documentada.
- Las tres variantes deben implementar exactamente las mismas dos tools (`nmap_scan`, `gobuster_dir`) sobre la misma Tier 0 para que la comparación sea válida.
- Los triggers de upgrade a MCP deben quedar explícitos y verificables en el `driver.md`, no implícitos en el código.

---

## 🐍 Python Project Template (estilo de Carlos Grande)

Esta sección define la estructura canónica y los patrones de código para cualquier proyecto Python. Seguir cada regla exactamente, sin desviaciones ni alternativas, salvo que el usuario lo solicite explícitamente.

> [!warning] Conflicto con esta PoC
> Esta PoC usa `uv` + `pyproject.toml` (no `requirements.txt`), variables de entorno (no `config.yaml`), y una estructura de directorios plana específica (`variant-*/`, `shared/`, `compare.py`). Esas desviaciones están documentadas en `outputs/tech-spec.md` y son intencionales. El **estilo de código** (headers, patrón `App`, clases, naming) sí aplica.

---

### Directory Structure

```
{project_name}/
├── data/
│   ├── config.yaml
│   └── logs/
│       └── file.log          # empty, created at runtime
├── src/
│   └── {package_name}/
│       ├── __init__.py        # empty
│       ├── main.py            # App class + entrypoint
│       └── <modules>.py       # one file per domain class
├── tests/
│   ├── __init__.py            # empty
│   └── test_<module>.py       # one test file per module
├── .gitignore
├── README.md
└── pyproject.toml
```

**Reglas:**
- Layout `src/` obligatorio — el package vive dentro de `src/{package_name}/`.
- `data/` contiene configuración y logs. Nunca datos dentro de `src/`.
- `tests/` es un sibling de `src/`, nunca anidado dentro.
- Sin `Dockerfile`, `.github/`, ni `docs/` salvo que se pidan explícitamente.

---

### File Header

Todo fichero `.py` empieza con este bloque exacto:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------
# Project: {project_name}
# Author/s: Carlos Grande
# Maintainer/s: Carlos Grande
# -----------------------------------------------------
```

`main.py` añade líneas adicionales tras el maintainer:

```python
# Date: DD/MM/YYYY
# License: Custom
# Version: 0.1.0
# Environment: {project_name}
# -----------------------------------------------------
```

---

### main.py — App Class Pattern

`main.py` contiene una única clase `App` y el entrypoint CLI. Es el **único** punto de entrada de la aplicación:

```python
# Libraries
import sys
import time
import argparse
import yaml
import structlog
from pydantic import BaseModel

# Classes
from .{module} import {ClassName}


# Config model — define project-specific fields here
class AppConfig(BaseModel):
    project_name: str
    path_logs: str


class App:
    """
    Class description: <one-line explanation>.
    Public methods: run
    """

    def __init__(self, args: argparse.Namespace):
        # Argument variables
        dir_config = args.config
        test = args.test
        arg_level = args.log[0]

        # Reading and validating the config yaml file
        with open(dir_config, 'r', encoding='utf8') as yaml_file:
            self.config = AppConfig(**yaml.safe_load(yaml_file))

        # Getting logger
        logger = self._get_logger(level=arg_level)

        # Logging argument variables
        logger.debug("initial_args", **vars(args))

        # Global variables
        self.log = logger

        # Global instances
        self.module = ClassName(logger=logger, config=self.config)

    def _get_logger(self, level: str) -> structlog.BoundLogger:
        import logging
        levels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING}
        logging.basicConfig(
            level=levels[level],
            format="%(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config.path_logs),
            ],
        )
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.dev.ConsoleRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger()

    def run(self):
        start_app = time.time()
        self.log.info(f"\033[1m[Initializing {self.config.project_name}]\033[0m")

        # >>> Application logic here <<<

        end_app = time.time()
        elapsed_time = end_app - start_app
        str_elapsed_time = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        self.log.info(f"\033[1m[Exiting {self.config.project_name} app. "
                      f"Total elapsed time: {str_elapsed_time}]\033[0m")
        sys.exit(0)


# Entrypoint
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c",
                        default="data/config.yaml",
                        help="Add the config file path after this flag")
    parser.add_argument('--log', "-l",
                        choices=['debug', 'info', 'warning'],
                        default=["info"],
                        nargs="+")
    parser.add_argument("--test", "-t",
                        default=False,
                        action='store_true',
                        help="This argument is a switcher, by default is false")
    my_args = parser.parse_args()

    my_app = App(args=my_args)
    my_app.run()
```

**Reglas duras para `main.py`:**
- `App` es siempre el único orquestador. Sin lógica fuera de esta clase (excepto el bloque `if __name__`).
- `AppConfig(BaseModel)` se define siempre en `main.py` o se importa desde un módulo `config.py`. Nunca se parsea el YAML a un `dict` plano.
- `_get_logger` es siempre un método privado de `App`, nunca una función standalone.
- Config se lee siempre desde YAML con `yaml.safe_load` y se valida con Pydantic en `__init__`.
- `run()` es siempre el método público de entrada. Mide el tiempo transcurrido y llama a `sys.exit(0)`.
- Los campos de config se acceden siempre con dot notation (`self.config.project_name`), nunca con claves de dict.
- Los imports de módulos hermanos usan siempre **imports relativos** (`from .module import Class`).

---

### Module Class Pattern

Todo módulo de dominio sigue este patrón:

```python
# Libraries
import structlog
from pydantic import BaseModel


class ClassName:
    """
    <One-line description of the class purpose.>
    """
    def __init__(self, logger: structlog.BoundLogger, config: BaseModel):
        # Global variables
        self.logger = logger
        self.config = config

    def _private_method(self):
        """<description>"""
        pass

    def public_method(self):
        """<description>"""
        pass
```

**Reglas duras para módulos:**
- Toda clase recibe `logger: structlog.BoundLogger` y `config: BaseModel` (subclase específica del proyecto) en `__init__`. Sin excepciones.
- Los almacena como `self.logger` y `self.config`.
- Métodos privados con prefijo `_`. Métodos públicos sin prefijo.
- Una clase por fichero. El nombre del fichero es el nombre de la clase en snake_case.
- Todas las clases se instancian en `App.__init__` y se llaman desde `App.run()`.

---

### config.yaml

```yaml
# Configuration file for the project {project_name}
# Author/s: Carlos Grande
# -----------------------------------------------------
# Date: DD/MM/YYYY
# License: Custom
# Version: 0.1.0
# Maintainer: Carlos Grande
# -----------------------------------------------------

# Configuration parameters
project_name: "{project_name}"
path_logs: data/logs/file.log

# >>> Add your configuration parameters here <<<
```

---

### pyproject.toml

```toml
[project]
name = "{project_name}"
version = "0.1.0"
description = "<one-line description>"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
    "pyyaml~=6.0",
    "structlog",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []
```

- `uv` es el gestor de paquetes. `uv sync` instala todas las dependencias.
- `pydantic>=2.0`, `pyyaml~=6.0` y `structlog` siempre presentes.
- Dependencias del proyecto bajo `dependencies`. Dev-only bajo `[tool.uv] dev-dependencies`.
- Nunca usar `requirements.txt` — `pyproject.toml` + `uv.lock` es la fuente de verdad.

---

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Project directory | kebab-case | `my-cool-tool` |
| Package directory | snake_case | `my_cool_tool` |
| Python files | snake_case | `data_processor.py` |
| Classes | PascalCase | `DataProcessor` |
| Functions/methods | snake_case | `process_data()` |
| Private methods | `_` prefix | `_validate_input()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |

---

### Checklist para agentes al crear un proyecto Python nuevo

1. Preguntar: nombre del proyecto, descripción en una línea, dependencias extra.
2. Generar el árbol de directorios exactamente como se define arriba.
3. Escribir `main.py` con el esqueleto de la clase `App`.
4. Escribir un fichero de módulo por dominio usando el patrón de clase.
5. Conectar todos los módulos en `App.__init__` y llamarlos desde `App.run()`.
6. Escribir `config.yaml` con `project_name` y `path_logs` más parámetros del proyecto.
7. Escribir `pyproject.toml` con `pydantic>=2.0`, `pyyaml~=6.0`, `structlog` más dependencias extra.
8. Escribir `.gitignore`, `tests/__init__.py` y `data/logs/file.log` vacío.
9. Escribir un `README.md` mínimo con nombre, descripción, instalación (`uv sync`) y uso.

> [!warning] Nunca desviar de esta estructura. No proponer patrones alternativos (p.ej. entrypoints funcionales, click/typer CLI, requirements.txt). Solo divergir si el usuario lo solicita explícitamente.
