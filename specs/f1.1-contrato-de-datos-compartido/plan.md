# Plan — F1.1 Contrato de datos compartido

## Enfoque

Se crea `shared/models.py` con dos modelos de input específicos por tool (`NmapScanInput`, `GobusterDirInput`) y un modelo de output común (`ToolResult`). El tipado estricto por tool permite generar JSON schemas válidos con `model_json_schema()` para las variantes V1 y V3. `ToolResult` con `extra: dict` garantiza paridad en la comparación sin contaminar el modelo base con campos específicos de cada tool.

## Implementación del paquete shared

- [ ] Crear el directorio `shared/` con `shared/__init__.py` vacío y `shared/models.py` con los imports base: `from pydantic import BaseModel, Field` y `from typing import Optional`.
- [ ] Implementar en `shared/models.py` las tres clases Pydantic: `NmapScanInput` (campos: `target: str`, `ports: str = "1-1000"`, `flags: list[str] = Field(default_factory=lambda: ["-sV"])`), `GobusterDirInput` (campos: `target: str`, `wordlist: str`, `extensions: list[str] = Field(default_factory=list)`) y `ToolResult` (campos: `raw_output: str`, `exit_code: int`, `error: Optional[str] = None`, `duration_ms: float`, `extra: dict = Field(default_factory=dict)`).

## Verificación

- [ ] Ejecutar `python -c "from shared.models import NmapScanInput, GobusterDirInput, ToolResult; s = NmapScanInput.model_json_schema(); assert 'target' in s['properties'] and 'ports' in s['properties'] and 'flags' in s['properties']; g = GobusterDirInput.model_json_schema(); assert 'target' in g['properties'] and 'wordlist' in g['properties']; r = ToolResult(raw_output='x', exit_code=0, duration_ms=1.0); assert r.error is None and r.extra == {}; print('OK')"` y confirmar que imprime `OK` con código de salida 0.
