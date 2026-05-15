<div align="center">

# 🛠️ windmark-poc-5-tools-contract

**PoC #5 — Contrato de invocación de tools**

_Tres variantes lado a lado · Decide ADR-003 del MVP de Windmark AI_

[![Status](https://img.shields.io/badge/status-in%20progress-yellow)](https://github.com/apt-404/windmark-poc-5-tools-contract)
[![Phase](https://img.shields.io/badge/phase-0%20%E2%80%94%20PoC-blue)](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/roadmap.md)
[![ADR](https://img.shields.io/badge/decides-ADR--003-purple)](https://github.com/apt-404/windmark-knowledge-base/blob/main/specs/mvp/tech-spec.md)
[![Issue](https://img.shields.io/badge/tracking-KB%20%236-lightgrey)](https://github.com/apt-404/windmark-knowledge-base/issues/6)
[![License](https://img.shields.io/badge/license-internal-black)](#)

</div>

---

## 🎯 Objetivo

Confirmar (o revisar) **ADR-003** del MVP de Windmark AI: ¿es **subprocess in-process con wrapper Pydantic** suficiente como contrato de invocación de tools para un MVP single-host con un único cliente del catálogo? ¿O hay que saltar ya a un MCP server local?

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

---

## 📦 Entregables

Este repo no es sólo código — es la **trazabilidad completa** de una decisión arquitectónica.

### 📄 Documentos

| Archivo | Contenido |
|---------|-----------|
| **`tech-spec.md`** | Arquitectura adoptada para cada variante · stack y versiones · contrato de invocación · configuración y pasos exactos para reproducir |
| **`report.md`** | Hipótesis evaluadas · experimentos ejecutados · métricas comparativas (coste de añadir una tool, tiempo de iteración, latencia, debuggability) · hallazgos cualitativos · limitaciones |
| **`driver.md`** | **Conclusión decisional** — contrato elegido · evidencia trazable al `report.md` · alternativas descartadas · triggers de upgrade a MCP · riesgos asumidos · puntos abiertos |

### 🧬 Artefactos reproducibles

- ✅ Tres prototipos lado a lado de `nmap_scan` y `gobuster_dir`
- ✅ Schema de tool-use generado en cada variante
- ✅ Trazas de invocación end-to-end

---

## ✅ Criterios de éxito

- [ ] **Equivalencia funcional** — tres implementaciones que resuelven lo mismo sobre la misma Tier 0
- [ ] **Métrica clara del coste** de añadir una tool nueva en cada variante
- [ ] **Triggers de migración a MCP** documentados de forma explícita y verificable

---

## 🚦 Triggers de upgrade a MCP

Tres condiciones que, si se cumplen, **invalidan ADR-003** y obligan a saltar a MCP server local:

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
| 🗺️ Roadmap | `windmark-knowledge-base/specs/mvp/roadmap.md` → `## 🧪 Phase 0 — Proof of Concepts` |
| 📐 ADR a decidir | `ADR-003` en `windmark-knowledge-base/specs/mvp/tech-spec.md` |

---

## 📁 Estructura del repo

```
windmark-poc-5-tools-contract/
├── README.md                    ← estás aquí
├── tech-spec.md                 ← cómo está implementado
├── report.md                    ← qué se probó y qué métricas salieron
├── driver.md                    ← la decisión final
├── variant-1-subprocess/        ← subprocess + Pydantic
│   ├── nmap_scan.py
│   └── gobuster_dir.py
├── variant-2-mcp-stdio/         ← MCP server stdio
│   ├── server.py
│   └── tools/
├── variant-3-native-tooluse/    ← tool-use nativo del provider
│   └── tools.py
└── traces/                      ← trazas de invocación end-to-end
```

> ⚠️ **Convivencia temporal.** Si este repo no existiera al cerrar la PoC, los tres documentos vivirían en `pocs/poc-5-tools-contract/` dentro del repo del MVP hasta extraerlos. Este repo es esa extracción.

---

<div align="center">

**Parte del programa interno** · [`apt-404`](https://github.com/apt-404) · Windmark AI

</div>
