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

### 📄 Documentos (en `outputs/`)

| Archivo | Contenido |
|---------|-----------|
| **[`outputs/product-spec.md`](outputs/product-spec.md)** | Alcance de la PoC · problema · principios de diseño · interfaces · criterios de éxito |
| **[`outputs/tech-spec.md`](outputs/tech-spec.md)** | Stack y versiones · módulos · ADRs propios de la PoC · setup Docker · integraciones |
| **[`outputs/report.md`](outputs/report.md)** | Hipótesis evaluadas · experimentos ejecutados · métricas comparativas (coste de añadir una tool, tiempo de iteración, latencia, debuggability) · hallazgos cualitativos · limitaciones |
| **[`outputs/driver.md`](outputs/driver.md)** | **Conclusión decisional** — contrato elegido · evidencia trazable al `report.md` · alternativas descartadas · triggers de upgrade a MCP · riesgos asumidos · puntos abiertos |

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

<div align="center">

**Parte del programa interno** · [`apt-404`](https://github.com/apt-404) · Windmark AI

</div>
