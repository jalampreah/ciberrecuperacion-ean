# Ciber-recuperación · Universidad Ean (92-EAN)

**Resiliencia frente a ransomware basada en integridad de datos** — laboratorios
open source con IA responsable. Un solo repositorio para todo el seminario: cada
semana se libera una sesión bajo su carpeta, reutilizando el mismo núcleo (`core/`).

> **Principio del curso:** el LLM es un **copiloto de análisis, no un piloto
> automático**, y **el tipo de dato decide dónde corre el modelo**. La evidencia
> no se envía a modelos públicos: se lleva **el modelo a la data** (local).

## Empezar (3 pasos)

```bash
git clone https://github.com/Hackwy402/ciberrecuperacion-ean.git
cd ciberrecuperacion-ean/core
bash setup.sh --local        # o --cloud   (ver core/README.md)
make check && make triage
```

Elige tu setup (3 caminos): [`core/docs/SETUP-1-local-vm.md`](core/docs/SETUP-1-local-vm.md) ·
[`core/docs/SETUP-2y3-cloud.md`](core/docs/SETUP-2y3-cloud.md).

## Índice de sesiones

| # | Carpeta | Sesión | Estado |
|---|---|---|---|
| 01 | [`01-ransomware-y-ciber-recuperacion/`](01-ransomware-y-ciber-recuperacion/) | Ransomware y ciber-recuperación — forense a mano + copiloto IA | ✅ Disponible |
| 02 | [`02-analisis-de-integridad-datos/`](02-analisis-de-integridad-datos/) | Análisis de integridad (entropía, hashing difuso, scoring) | ✅ Disponible |
| 03 | [`03-deteccion-variantes-yara-sigma-ia/`](03-deteccion-variantes-yara-sigma-ia/) | Detección de variantes con IA (YARA/Sigma) | ✅ Disponible |
| 04 | [`04-boveda-inmutable-worm/`](04-boveda-inmutable-worm/) | Bóveda inmutable (MinIO Object Lock, restic/Borg, FIM) | ✅ Disponible |
| 05 | [`05-copiloto-recuperacion-rag/`](05-copiloto-recuperacion-rag/) | Copiloto de recuperación (RAG, Velociraptor, RTO/RPO) | ⏳ |

## Estructura del repositorio

```
ciberrecuperacion-ean/
├── core/                                   # kit reutilizable (setup, cliente LLM, Makefile, docs)
├── 01-ransomware-y-ciber-recuperacion/     # SESIÓN 1 (disponible)
│   ├── parte-1-forense-manual.md           #   análisis con comandos
│   ├── parte-2-copiloto-ia.md              #   análisis asistido por IA local
│   ├── scripts/  datasets/                 #   generador de dataset + entropía
│   ├── diapositivas/                       #   deck de teoría (pptx + pdf) y guía del lab
│   └── SOLUCION-docente.md
├── 02-…  03-…  04-…  05-…                   # se liberan semana a semana
├── docs/                                   # material transversal (modelos, matriz datos→backend)
├── SETUP-DEMO-docente.md                   # runbook de comandos (local + Ubuntu)
└── README.md
```

## Referencias del curso

- Selección de modelo y hardware: [`docs/modelos-abiertos-y-hardware.md`](docs/modelos-abiertos-y-hardware.md)
- Regla forense datos → backend: [`docs/matriz-datos-backend.md`](docs/matriz-datos-backend.md)
- Panorama de herramientas (mercado, nube AWS/Azure y nuestro lab): [`docs/panorama-herramientas-integridad.md`](docs/panorama-herramientas-integridad.md)
- Backups en la nube (AWS/Azure, herramientas nativas): [`docs/backups-nube-aws-azure.md`](docs/backups-nube-aws-azure.md)

---

Universidad Ean · Educación Continua · Docente: Jawy Andrés Romero Pinto
Material educativo. Datasets 100% sintéticos; ninguno es evidencia real.
