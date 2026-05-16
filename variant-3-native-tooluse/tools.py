NMAP_SCAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "nmap_scan",
        "description": "Run an nmap scan against a target host or IP range and return open ports and service fingerprints.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Target host or IP range to scan.",
                },
                "ports": {
                    "type": "string",
                    "description": "Port specification (e.g. '22,80,443' or '1-1000').",
                },
                "flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional nmap CLI flags.",
                },
            },
            "required": ["target"],
        },
    },
}


GOBUSTER_DIR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "gobuster_dir",
        "description": "Run gobuster in dir mode against a target URL to discover directories and files using a wordlist.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Target URL to brute-force (e.g. 'http://example.com').",
                },
                "wordlist": {
                    "type": "string",
                    "description": "Path to the wordlist file.",
                },
                "extensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File extensions to append to each word (e.g. ['php', 'html']).",
                },
            },
            "required": ["target", "wordlist"],
        },
    },
}
