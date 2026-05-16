<div align="center">

# 🛠️ windmark-poc-5-tools-contract

**PoC #5 — Contrato de invocación de tools**

_Tres variantes lado a lado · Decide ADR-003 del MVP de Windmark AI_

[![Status](https://img.shields.io/badge/status-in%20progress-yellow)](https://github.com/apt-404/windmark-poc-5-tools-contract)
[![Phase](https://img.shields.io/badge/phase-0%20%E2%80%94%20PoC-blue)](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/roadmap.md#poc-5----contrato-de-invocación-de-tools-p)
[![ADR](https://img.shields.io/badge/decides-ADR--003-purple)](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md#adr-003-tools-in-process-con-subprocess-rechazo-de-mcp-en-mvp)
[![Issue](https://img.shields.io/badge/tracking-KB%20%236-lightgrey)](https://github.com/apt-404/windmark-knowledge-base/issues/6)
[![License](https://img.shields.io/badge/license-internal-black)](#)

</div>

---

## 🎯 Objetivo

Confirmar (o revisar) **[ADR-003](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md#adr-003-tools-in-process-con-subprocess-rechazo-de-mcp-en-mvp)** del MVP de Windmark AI: ¿es **subprocess in-process con wrapper Pydantic** suficiente como contrato de invocación de tools para un MVP single-host con un único cliente del catálogo? ¿O hay que saltar ya a un MCP server local?

> **Hipótesis de partida.** Para el MVP, subprocess+Pydantic es suficiente. MCP server local sólo aporta cuando aparece un **segundo cliente del catálogo** o se necesita **aislamiento por blast radius**.

---

## 🧪 Las tres variantes

| # | Variante | Qué prueba | Coste percibido |
|---|----------|------------|-----------------|
| 1 | **subprocess + Pydantic** | Wrapper in-process, schema generado desde modelos Pydantic | 🟢 Bajo |
| 2 | **MCP server stdio** | Tool server local hablando MCP por stdio | 🟡 Medio |
| 3 | **tool-use nativo del provider** | Schema entregado directo al LLM (Anthropic / OpenAI tool-use) | 🟢 Bajo |

Cada variante implementa **las mismas dos tools sobre la misma Tier 0**:

```
┌────────────────────┐      ┌────────────────────┐
│   nmap_scan        │      │   gobuster_dir     │
│   (reconocimiento) │      │   (descubrimiento) │
└────────────────────┘      └────────────────────┘
```

### Flujo de ejecución por variante

Lo que diferencia las tres variantes es **qué proceso llega a la víctima** y **quién decide los parámetros de invocación**.

```
V1 — subprocess + Pydantic (in-process)

  [Agente] ──import──► tool() ──subprocess──► víctima
  └─────────────────── mismo proceso ─────────────────┘

  El propio proceso del agente abre el subprocess y llega a la víctima.


V2 — MCP server stdio (proceso separado)

  [Agente] ──JSON-RPC (stdio)──► [MCP Server] ──subprocess──► víctima
                                 └── proceso hijo del agente ──────────┘

  El MCP Server es un proceso hijo levantado por el agente (Popen).
  Es el Server, no el agente, quien llega a la víctima.
  Con stdio: 1 agente = 1 MCP server (no se puede compartir entre agentes).


V3 — Tool-use nativo del provider

  [Agente] ──schema──► [LLM API] ──tool_use block──► [Agente] ──subprocess──► víctima
                        └─ decide cuándo y params ─┘  └───── mismo proceso ──────────┘

  El LLM nunca toca la red: solo devuelve la decisión de invocación.
  El agente ejecuta el subprocess (igual que V1). El LLM API es compartida.

  En esta PoC el LLM está mockeado con fixtures pregrabadas:
  [Agente] ──lee fixture JSON──► params ──subprocess──► víctima
```

| Variante | ¿Quién llega a la víctima? | ¿Quién decide los params? | N agentes → |
|----------|--------------------------|--------------------------|-------------|
| V1 | El agente (in-process) | El agente (caller directo) | N procesos independientes |
| V2 | El MCP Server (proceso hijo) | El agente (cliente MCP) | N servers (1 por agente, stdio) |
| V3 | El agente (in-process) | El LLM (vía tool_use block) | N agentes, 1 LLM API compartida |

---

## 📚 Especificaciones de referencia (KB)

Documentos del knowledge base que esta PoC lee, implementa y decide:

| Documento | Descripción |
|-----------|-------------|
| [**`specs/mvp/product-spec.md`**](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/product-spec.md) | Visión del MVP, principios de diseño, arquitectura objetivo, interfaces CLI y out-of-scope |
| [**`specs/mvp/tech-spec.md`**](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md) | Stack técnico, módulos, ADRs (incluyendo **ADR-003** que esta PoC decide), discovery items |
| [**`specs/mvp/roadmap.md`**](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/roadmap.md) | Fase 0 (PoCs), Fase 1 (Tiers), dependency graph completo y gates de cierre |

---

## 📦 Entregables

Este repo no es sólo código — es la **trazabilidad completa** de una decisión arquitectónica.

### 📐 Specs (en `specs/`)

| Archivo | Contenido |
|---------|-----------|
| **[`specs/product-spec.md`](specs/product-spec.md)** | Visión de la PoC · problema · usuarios · principios de diseño · arquitectura · interfaces · criterios de éxito · out of scope |
| **[`specs/tech-spec.md`](specs/tech-spec.md)** | Stack y versiones · topología de módulos · contrato de datos · ADRs propios de la PoC · setup Docker · known limitations |
| **[`specs/roadmap.md`](specs/roadmap.md)** | Fases · features · dependency graph · gates de cierre |

### 📄 Outputs (en `outputs/`)

| Archivo | Contenido |
|---------|-----------|
| **[`outputs/product-spec.md`](outputs/product-spec.md)** | Alcance de la PoC · problema · principios de diseño · interfaces · criterios de éxito |
| **[`outputs/tech-spec.md`](outputs/tech-spec.md)** | Stack y versiones · módulos · ADRs propios de la PoC · setup Docker · integraciones |
| **[`outputs/report.md`](outputs/report.md)** | Condiciones del run · hipótesis evaluadas · métricas comparativas · hallazgos · limitaciones |
| **[`outputs/report.html`](outputs/report.html)** | Dashboard visual del `report.md` — barras de latencia, token footprint, hipótesis y tabla detallada |
| **[`outputs/variants-clarifications.md`](outputs/variants-clarifications.md)** | Aclaración de alcance por variante — qué cubre cada implementación, sus limitaciones y qué queda fuera de scope |
| **[`outputs/driver.md`](outputs/driver.md)** | **Conclusión decisional** — contrato elegido · evidencia trazable al `report.md` · triggers de upgrade a MCP · riesgos asumidos |

### 🧬 Artefactos reproducibles

- ✅ Tres prototipos lado a lado de `nmap_scan` y `gobuster_dir`
- ✅ Schema de tool-use generado en cada variante
- ✅ Trazas de invocación end-to-end en `traces/`

---

## ✅ Criterios de éxito

- [ ] **Equivalencia funcional** — tres implementaciones que resuelven lo mismo sobre la misma Tier 0
- [ ] **Métrica clara del coste** de añadir una tool nueva en cada variante
- [ ] **Triggers de migración a MCP** documentados de forma explícita y verificable

---

## 🚦 Triggers de upgrade a MCP

Tres condiciones que, si se cumplen, **invalidan [ADR-003](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md#adr-003-tools-in-process-con-subprocess-rechazo-de-mcp-en-mvp)** y obligan a saltar a MCP server local:

> 🔁 **Segundo cliente del catálogo** — más de un consumidor de las mismas tools.
> 🛡️ **Aislamiento por blast radius** — necesidad de ejecutar tools en un container separado.
> 💼 **Demanda comercial temprana** — un cliente externo pide MCP como contrato.

---

## 🗺️ Ubicación en el roadmap

```
Phase 0 — Proof of Concepts
├── PoC #1 ─┐
├── PoC #2 ─┤  paralelizables
├── PoC #3 ─┤
├── PoC #5 ◀── ESTE REPO  ────► bloquea a PoC #4
└── PoC #6 ─┘
```

| Tipo | Referencia |
|------|------------|
| 🐛 Issue tracking | [`apt-404/windmark-knowledge-base#6`](https://github.com/apt-404/windmark-knowledge-base/issues/6) |
| 🗺️ Roadmap | [`specs/mvp/roadmap.md → PoC #5`](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/roadmap.md#poc-5----contrato-de-invocación-de-tools-p) |
| 📐 ADR a decidir | [`ADR-003` en `specs/mvp/tech-spec.md`](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md#adr-003-tools-in-process-con-subprocess-rechazo-de-mcp-en-mvp) |

---

## 📁 Estructura del repo

```
windmark-poc-5-tools-contract/
├── README.md                        ← estás aquí
├── AGENTS.md                        ← documentos de referencia del KB para agentes
├── compare.py                       ← runner de comparación entre variantes
├── Dockerfile                       ← imagen con Python 3.12 + uv + nmap + gobuster
├── outputs/                         ← todos los documentos de la PoC
│   ├── product-spec.md              ← alcance, principios, interfaces, criterios de éxito
│   ├── tech-spec.md                 ← stack, módulos, ADRs, setup local
│   ├── report.md                    ← métricas comparativas y hallazgos
│   ├── report.html                  ← versión visual del report con tablas y gráficas
│   ├── variants-clarification.md    ← aclaración de alcance y limitaciones por variante
│   └── driver.md                    ← decisión final sobre ADR-003
├── shared/
│   └── models.py                    ← ToolInput y ToolResult compartidos entre variantes
├── variant-1-subprocess/            ← subprocess + Pydantic in-process
│   ├── nmap_scan.py
│   └── gobuster_dir.py
├── variant-2-mcp-stdio/             ← MCP server stdio (FastMCP)
│   ├── server.py
│   └── tools/
├── variant-3-native-tooluse/        ← tool-use nativo, schema OpenAI via LiteLLM
│   └── tools.py
└── traces/                          ← trazas de invocación end-to-end
    ├── fixtures/                    ← respuestas Claude CLI pregrabadas (mocks LLM)
    ├── v1/
    ├── v2/
    ├── v3/
    └── metrics.json                 ← consolidado comparativo
```

---

## 🚀 Ejecución manual (WSL)

### 1. Prerrequisitos del sistema

```bash
# Herramientas de reconocimiento
sudo apt update
sudo apt install -y nmap gobuster

# Wordlist (dirb/common.txt que usa compare.py por defecto)
sudo apt install -y dirb

# uv — gestor de paquetes Python
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc   # o reinicia el terminal
```

### 2. Instalar dependencias Python

```bash
# Desde la raíz del repo
uv sync --frozen
```

Esto instala `pydantic`, `fastmcp`, `litellm` y `structlog` en el virtualenv de uv.

### 3. Conectar a la VPN de HTB

```bash
sudo openvpn --config ~/.config/htb/lab-htb.ovpn &
# Espera a ver "Initialization Sequence Completed"
# Comprueba que tienes conectividad
ping -c 1 $TARGET_IP
```

### 4. Variables de entorno

```bash
export TARGET_IP=10.10.11.X
export WORDLIST_PATH=/usr/share/wordlists/dirb/common.txt
```

### 5. Verificar entorno

```bash
uv run python compare.py --check
```

Salida esperada — todas las filas deben mostrar `OK`:

```
+------------------------------------------+--------+
| Dependencia                              | Estado |
+------------------------------------------+--------+
| nmap                                     | OK     |
| gobuster                                 | OK     |
| wordlist (/usr/share/wordlists/...)      | OK     |
| fixtures (traces/fixtures/*.json)        | OK     |
| ping 10.10.11.X                          | OK     |
+------------------------------------------+--------+
```

> **Nota — `ping ERROR` en targets HTB.** Muchas máquinas de HTB bloquean ICMP, por lo que el check puede reportar `ping ERROR` aunque la conectividad sea correcta. Para verificar que el target es alcanzable usa nmap:
> ```bash
> nmap -Pn -p 22,80,443 $TARGET_IP
> ```
> Si nmap devuelve `Host is up`, puedes lanzar la PoC con normalidad — el `ping ERROR` del check no bloquea la ejecución.

### 6. Lanzar la comparación

**Todas las variantes y tools (ejecución completa):**

```bash
uv run python compare.py --target $TARGET_IP
```

**Variante y tool concretas:**

```bash
# Solo V1 con nmap
uv run python compare.py --target $TARGET_IP --variant v1 --tool nmap_scan

# Solo V2 con gobuster
uv run python compare.py --target $TARGET_IP --variant v2 --tool gobuster_dir
```

**Con repeticiones para métricas de latencia:**

```bash
uv run python compare.py --target $TARGET_IP --repeat 3
```

**Directorio de salida personalizado:**

```bash
uv run python compare.py --target $TARGET_IP --output traces/run-htb/
```

### 7. Resultados

```
traces/
├── v1/nmap_scan/<timestamp>.jsonl     ← traza por invocación
├── v1/gobuster_dir/<timestamp>.jsonl
├── v2/...
├── v3/...
└── metrics.json                       ← consolidado con duration_ms y summary
```

`metrics.json` incluye `duration_ms_mean` y `duration_ms_values` por combinación `(variante, tool)` cuando se usa `--repeat > 1`.

---

<div align="center">

**Parte del programa interno** · [`apt-404`](https://github.com/apt-404) · Windmark AI

</div>
