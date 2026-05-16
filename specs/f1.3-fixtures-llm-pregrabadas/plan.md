# Plan — F1.3 Fixtures LLM pregrabadas

## Enfoque

Se generan dos fixtures estáticas en formato OpenAI `function_call` para simular la respuesta del LLM en V3. Los archivos se escriben directamente en `traces/fixtures/` con la estructura conocida del formato OpenAI y se commitean en el repositorio. Las fixtures no se regeneran en tiempo de ejecución del runner.

## Creación de fixtures

- [x] Crear el directorio `traces/fixtures/` y `traces/.gitkeep` si el directorio `traces/` no está aún rastreado por git; escribir `traces/fixtures/nmap_scan.json` con la estructura `{"id": "call_nmap_scan_001", "type": "function", "function": {"name": "nmap_scan", "arguments": "{\"target\": \"192.168.1.1\", \"ports\": \"1-1000\", \"flags\": [\"-sV\"]}"}}` y `traces/fixtures/gobuster_dir.json` con la estructura análoga para `gobuster_dir` con campos `target`, `wordlist` y `extensions`.

## Tests

- [ ] Crear `tests/test_fixtures.py` con dos funciones pytest derivadas de los Criterios de Aceptación de `requirements.md`: `test_nmap_fixture_structure()` carga `traces/fixtures/nmap_scan.json`, parsea `function.arguments` y verifica que contiene `target == "192.168.1.1"`, `ports == "1-1000"` y `flags == ["-sV"]`; `test_gobuster_fixture_structure()` carga `traces/fixtures/gobuster_dir.json` y verifica que `function.arguments` contiene las claves `target`, `wordlist` y `extensions`.
- [ ] Ejecutar `pytest tests/test_fixtures.py -v` y confirmar exit code 0.
