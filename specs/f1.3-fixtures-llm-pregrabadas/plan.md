# Plan — F1.3 Fixtures LLM pregrabadas

## Enfoque

Se generan dos fixtures estáticas en formato OpenAI `function_call` para simular la respuesta del LLM en V3. Los archivos se escriben directamente en `traces/fixtures/` con la estructura conocida del formato OpenAI y se commitean en el repositorio. Las fixtures no se regeneran en tiempo de ejecución del runner.

## Creación de fixtures

- [ ] Crear el directorio `traces/fixtures/` y `traces/.gitkeep` si el directorio `traces/` no está aún rastreado por git; escribir `traces/fixtures/nmap_scan.json` con la estructura `{"id": "call_nmap_scan_001", "type": "function", "function": {"name": "nmap_scan", "arguments": "{\"target\": \"192.168.1.1\", \"ports\": \"1-1000\", \"flags\": [\"-sV\"]}"}}` y `traces/fixtures/gobuster_dir.json` con la estructura análoga para `gobuster_dir` con campos `target`, `wordlist` y `extensions`.

## Verificación

- [ ] Ejecutar `python -c "import json; n = json.load(open('traces/fixtures/nmap_scan.json')); args = json.loads(n['function']['arguments']); assert args['target'] == '192.168.1.1' and args['ports'] == '1-1000' and args['flags'] == ['-sV']; g = json.load(open('traces/fixtures/gobuster_dir.json')); gargs = json.loads(g['function']['arguments']); assert 'target' in gargs and 'wordlist' in gargs and 'extensions' in gargs; print('OK')"` y confirmar `OK` con código de salida 0.
- [ ] Ejecutar `python compare.py --check` y confirmar que stdout contiene la línea de fixtures con estado OK y que el código de salida refleja el estado real del entorno.
