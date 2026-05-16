# Plan — F1.3 Fixtures LLM pregrabadas

## Enfoque

Se generan dos fixtures estáticas en formato OpenAI `function_call` para simular la respuesta del LLM en V3. El proceso es: usar claude CLI para obtener un ejemplo de respuesta real y entender la estructura, luego escribir los archivos finales en formato OpenAI `function_call` en `traces/fixtures/`. Las fixtures se commitean en el repositorio y no se regeneran en tiempo de ejecución del runner.

## Directorio de fixtures

- [ ] Crear el directorio `traces/fixtures/` en la raíz del proyecto.
- [ ] Crear `traces/.gitkeep` si el directorio `traces/` no está aún rastreado por git, para que la carpeta quede en el repositorio.

## Generación de referencia con claude CLI

- [ ] Ejecutar `claude --output-format json "Necesito invocar la tool nmap_scan con target 192.168.1.1, ports 1-1000 y flags -sV"` y examinar la estructura del output para entender el formato de respuesta del CLI.
- [ ] Ejecutar `claude --output-format json "Necesito invocar la tool gobuster_dir con target http://192.168.1.1 y wordlist /usr/share/wordlists/dirb/common.txt"` y examinar el output.

## Escritura de fixtures en formato OpenAI

- [ ] Crear `traces/fixtures/nmap_scan.json` con la estructura: `{"id": "call_nmap_scan_001", "type": "function", "function": {"name": "nmap_scan", "arguments": "{\"target\": \"192.168.1.1\", \"ports\": \"1-1000\", \"flags\": [\"-sV\"]}"}}`.
- [ ] Crear `traces/fixtures/gobuster_dir.json` con la estructura análoga: `{"id": "call_gobuster_dir_001", "type": "function", "function": {"name": "gobuster_dir", "arguments": "{\"target\": \"http://192.168.1.1\", \"wordlist\": \"/usr/share/wordlists/dirb/common.txt\", \"extensions\": []}"}}`.

## Verificación

- [ ] Ejecutar `python -c "import json; d = json.load(open('traces/fixtures/nmap_scan.json')); args = json.loads(d['function']['arguments']); print(args)"` y verificar que imprime `{'target': '192.168.1.1', 'ports': '1-1000', 'flags': ['-sV']}`.
- [ ] Ejecutar lo mismo con `gobuster_dir.json` y verificar que los parámetros `target`, `wordlist` y `extensions` están presentes y son correctos.
- [ ] Ejecutar `python compare.py --check` y verificar que el check de fixtures aparece como OK en la tabla de estado.
