# Plan — F1.1 Contrato de datos compartido

## Enfoque

Se crea `shared/models.py` con dos modelos de input específicos por tool (`NmapScanInput`, `GobusterDirInput`) y un modelo de output común (`ToolResult`). El tipado estricto por tool permite generar JSON schemas válidos con `model_json_schema()` para las variantes V1 y V3. `ToolResult` con `extra: dict` garantiza paridad en la comparación sin contaminar el modelo base con campos específicos de cada tool.

## Setup y estructura

- [ ] Crear el directorio `shared/` en la raíz del proyecto.
- [ ] Crear `shared/__init__.py` vacío para que el directorio sea importable como paquete Python.
- [ ] Crear `shared/models.py` con el esqueleto de imports: `from pydantic import BaseModel` y `from typing import Optional`.

## Implementación de modelos

- [ ] Añadir en `shared/models.py` la clase `NmapScanInput(BaseModel)` con campos: `target: str`, `ports: str = "1-1000"`, `flags: list[str] = Field(default_factory=lambda: ["-sV"])`.
- [ ] Añadir en `shared/models.py` la clase `GobusterDirInput(BaseModel)` con campos: `target: str`, `wordlist: str`, `extensions: list[str] = Field(default_factory=list)`.
- [ ] Añadir en `shared/models.py` la clase `ToolResult(BaseModel)` con campos: `raw_output: str`, `exit_code: int`, `error: Optional[str] = None`, `duration_ms: float`, `extra: dict = Field(default_factory=dict)`.

## Verificación

- [ ] Ejecutar `python -c "from shared.models import NmapScanInput, GobusterDirInput, ToolResult; print('OK')"` y confirmar que imprime `OK` sin errores de importación.
- [ ] Ejecutar `python -c "from shared.models import NmapScanInput; import json; print(json.dumps(NmapScanInput.model_json_schema(), indent=2))"` y verificar que el schema contiene los campos `target`, `ports`, `flags` con tipos y defaults correctos.
- [ ] Ejecutar `python -c "from shared.models import GobusterDirInput; import json; print(json.dumps(GobusterDirInput.model_json_schema(), indent=2))"` y verificar que contiene `target`, `wordlist`, `extensions`.
- [ ] Ejecutar `python -c "from shared.models import ToolResult; r = ToolResult(raw_output='x', exit_code=0, duration_ms=1.0); print(r.error, r.extra)"` y verificar que imprime `None {}`.
