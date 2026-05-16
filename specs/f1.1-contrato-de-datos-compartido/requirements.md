# F1.1 — Contrato de datos compartido

## Contexto

El runner y las tres variantes necesitan operar sobre tipos de datos idénticos para que la comparación entre variantes sea válida. `shared/models.py` define los modelos Pydantic de entrada y salida que actúan como única fuente de verdad del contrato, eliminando la posibilidad de divergencia silenciosa entre variantes (ADR-002).

## Criterios de aceptación

- [ ] `shared/models.py` define `NmapScanInput` y `GobusterDirInput` como modelos Pydantic con los campos y defaults del product-spec.
- [ ] `shared/models.py` define `ToolResult` con los campos: `raw_output: str`, `exit_code: int`, `error: Optional[str] = None`, `duration_ms: float`, `extra: dict = {}`.
- [ ] `NmapScanInput.model_json_schema()` genera un JSON schema válido con campos, tipos y defaults correctos.
- [ ] `GobusterDirInput.model_json_schema()` genera un JSON schema válido con campos, tipos y defaults correctos.
- [ ] Las tres variantes y el runner importan exclusivamente de `shared/models.py`; ninguna variante define sus propios tipos de datos.
- [ ] El módulo solo depende de `pydantic` y stdlib (sin dependencias de runtime adicionales).

## Fuera de alcance

- Subclases o variantes de `ToolResult` por tool (los datos específicos de cada tool van en `extra: dict`).
- Funciones helper de generación de schema en `shared/` (cada variante llama `model_json_schema()` directamente).
- Validación de valores concretos de parámetros (p.ej. que `ports` sea un rango válido de nmap); solo tipos y defaults.

## Dependencias

| Dep | Tipo | Estado |
|-----|------|--------|
| — | — | — |

## Decisiones tomadas

| Decisión | Opción elegida | Alternativa descartada |
|----------|----------------|------------------------|
| Estructura de ToolInput | Subclases por tool (`NmapScanInput`, `GobusterDirInput`) | Modelo genérico con `params: dict` |
| Estructura de ToolResult | Campos genéricos + `extra: dict = {}` (ADR-002) | Campos específicos por tool directamente en ToolResult |
| Campo error en ToolResult | `Optional[str] = None` | `str = ""` |
| Generación de JSON schema | Cada variante llama `model_json_schema()` directamente | Helper centralizado `get_tool_schema()` en `shared/` |
