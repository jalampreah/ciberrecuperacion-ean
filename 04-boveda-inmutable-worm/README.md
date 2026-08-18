# Sesión 4 · Bóveda inmutable (WORM)

De **detectar** al actor (Sesión 3) a garantizar **desde dónde restaurar**: una
copia que el ransomware **no puede destruir aunque tenga tus credenciales de
administrador**. Object Lock (WORM), repositorios **append-only** y snapshots.

Caso: el mismo actor de la Sesión 3 ya está dentro con credenciales robadas y su
siguiente objetivo son los backups. Hoy construyes la copia que sobrevive a eso.

## Flujo del taller (dos tiempos)

1. **Setup:** entorno del kit (`../core`) con Docker: `setup.sh --with-docker`.
   Levanta los servicios del módulo: `docker compose up -d` (MinIO + rest-server).
2. **Parte 1 — Bóveda WORM:** [`parte-1-boveda-worm.md`](parte-1-boveda-worm.md)
   MinIO + S3 Object Lock en modo COMPLIANCE. Bucket normal vs bóveda ante el
   **mismo** ataque: el borrado rebota con *"Object is WORM protected"*.
3. **Parte 2 — Append-only:** [`parte-2-append-only-restic.md`](parte-2-append-only-restic.md)
   Repositorio `restic` publicado con `--append-only`: el cliente comprometido
   puede respaldar y restaurar, pero su `forget --prune` malicioso rebota con
   `403 Forbidden`. El servidor manda, no el cliente.
4. **Parte 3 — Vigilar y restaurar:** [`parte-3-fim-y-restauracion.md`](parte-3-fim-y-restauracion.md)
   **AIDE** (FIM) detecta la manipulación de la carpeta de backup; restauras
   desde la bóveda y verificas con hashes (mismo scoring de la Sesión 2). El
   "0" de la regla 3-2-1-1-0.

## Contenido

```
04-boveda-inmutable-worm/
├── parte-1-boveda-worm.md          # MinIO + Object Lock (WORM)
├── parte-2-append-only-restic.md   # restic + rest-server append-only
├── parte-3-fim-y-restauracion.md   # AIDE (FIM) + restauración verificada
├── SOLUCION-docente.md             # (no se publica) comandos + salidas esperadas
├── docker-compose.yml              # minio + rest-server (servicios del lab)
├── scripts/
│   ├── generar_dataset.py          # datos de "producción" + manifiesto SHA-256 (sin deps)
│   ├── atacar_boveda.sh            # el "ransomware": intenta destruir el backup con tus llaves
│   └── verificar_integridad.py     # scoring de integridad de la restauración (sin deps)
└── datasets/caso4/                 # generado: produccion/ + manifiesto_sha256.json
```

## Conceptos

La regla **3-2-1-1-0** (el "1" inmutable y el "0" de verificación), WORM de la
cinta al **Object Lock** por software (modos GOVERNANCE vs COMPLIANCE),
**append-only** (el servidor decide, no el cliente), **snapshots ZFS**
(copy-on-write + `zfs hold`) y **FIM** con AIDE / Wazuh como la "cámara de
seguridad" del backup.

MITRE ATT&CK del caso: **T1490** (inhibir la recuperación) — el mismo que
detectabas con Sigma en la Sesión 3, ahora mitigado por diseño.

Los datos son **100 % sintéticos**. El "ataque" es un script que usa **tus
credenciales válidas**: si la bóveda resiste eso, resiste al ransomware real.
Requiere Docker (Parte 1 y 2); AIDE se instala en la Parte 3 (hay fallback en
Python). Los scripts del lab no tienen dependencias más allá de la stdlib.
