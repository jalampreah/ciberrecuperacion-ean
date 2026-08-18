# Parte 2 · Append-only: el servidor decide, no el cliente (restic)

**Taller Sesión 4 · Ciber-Recuperación (92-EAN)** · Duración: 25 min

> Object Lock protege objetos en almacenamiento S3. Pero muchos backups viven en
> un **repositorio** (restic, Borg) al que un host de backup accede con una
> llave. Si ese host cae ante el ransomware, su llave puede **podar la historia**
> (`forget --prune`). La respuesta: que el **servidor** publique el repo en modo
> **append-only** — el cliente añade, nunca destruye.

## 1. Conoce el terreno

En el `docker compose` ya corre `rest-server` (el servidor de repos de restic)
publicado con la opción **`--append-only`** (míralo en `docker-compose.yml`):

```yaml
rest-server:
  environment:
    OPTIONS: "--no-auth --append-only"
```

Instala el cliente `restic` en tu host:

```bash
# Ubuntu:  sudo apt install -y restic     |    macOS:  brew install restic
restic version
```

Apunta restic al servidor del lab (variables de entorno):

```bash
export RESTIC_REPOSITORY="rest:http://localhost:8000/"
export RESTIC_PASSWORD="lab123"
restic init                       # inicializa el repositorio
```

## 2. Respalda producción (el flujo normal, permitido)

```bash
restic backup datasets/caso4/produccion --host lab
restic snapshots                  # deberia listar 1 snapshot con su short-id
```

Haz un segundo backup para tener historia (cambia algo primero):

```bash
echo "nota extra" >> datasets/caso4/produccion/ti/runbook_recuperacion.md
restic backup datasets/caso4/produccion --host lab
restic snapshots                  # ahora 2 snapshots
```

## 3. El ataque: el cliente comprometido intenta borrar la historia (10 min)

El ransomware en el host de backup haría exactamente esto — quedarse con el
snapshot más nuevo (ya cifrado) y **podar** los limpios:

```bash
SNAP=$(restic snapshots --json | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['short_id'])")
restic forget "$SNAP" --prune
```

Respuesta del servidor:

```
Remove(<snapshot/...>) failed: unexpected HTTP response (403): 403 Forbidden
unable to remove snapshot ... from the repository
```

**Denegado.** El cliente tiene la llave del repo, pero el **servidor** no le
permite borrar. La poda legítima la haría *otro* host de confianza, programado,
nunca el que respalda producción.

> Restic imprime un rastro de error después del `403`. El mensaje que importa es
> el `403 Forbidden` de la primera línea: ahí rebotó el ataque.

## 4. Lo que SÍ puede hacer el cliente: restaurar (5 min)

Append-only no estorba la recuperación — solo prohíbe destruir:

```bash
restic restore "$SNAP" --target /tmp/restaurado
ls -R /tmp/restaurado/            # producción restaurada intacta
restic check                      # "no errors were found" — el repo está sano
```

## 5. Compáralo: el mismo ataque en un repo desprotegido (opcional)

Para sentir la diferencia, un repo local **sin** append-only sí deja podar:

```bash
export RESTIC_REPOSITORY="/tmp/repo-inseguro"
restic init && restic backup datasets/caso4/produccion --host lab
SNAP2=$(restic snapshots --json | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['short_id'])")
restic forget "$SNAP2" --prune    # aquí SÍ borra: adiós historial
```

Vuelve a apuntar a la bóveda cuando termines:
`export RESTIC_REPOSITORY="rest:http://localhost:8000/"`.

> ✅ **Checkpoint Parte 2:** el `forget --prune` malicioso rebotó con `403` en el
> repo append-only, pero backup y restore siguieron funcionando. Entiendes la
> diferencia entre "la llave hace todo" y "el servidor decide". Sigue la Parte 3:
> ¿cómo te enteras de que alguien tocó la bóveda? → **FIM**.
