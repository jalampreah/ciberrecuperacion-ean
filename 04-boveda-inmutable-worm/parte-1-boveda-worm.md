# Parte 1 · La bóveda WORM (MinIO + Object Lock)

**Taller Sesión 4 · Ciber-Recuperación (92-EAN)** · Duración: 30 min
Entorno: **Ubuntu** (VM local, Azure o WSL2) o **macOS**, con **Docker**.

> En la Sesión 3 detectaste al actor. Hoy asumes lo peor: **ya está dentro con
> tus credenciales de administrador** y va por los backups. Vas a construir la
> copia que sobrevive a eso — y a atacarla tú mismo para comprobarlo.

## 0. Levanta los servicios del lab

```bash
cd 04-boveda-inmutable-worm
python3 scripts/generar_dataset.py     # datos sinteticos de "produccion" + manifiesto
docker compose up -d                   # MinIO (:9000/:9001) + rest-server (:8000)
docker compose ps                      # ambos "running"/"healthy"
```

Instala el cliente `mc` de MinIO (si no lo tienes en el host):

```bash
# Ubuntu / Linux
curl -sO https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x mc && sudo mv mc /usr/local/bin/
# macOS:  brew install minio-mc

mc alias set local http://localhost:9000 labadmin labadmin123
```

> Las credenciales `labadmin/labadmin123` son de laboratorio (van en el
> `docker-compose.yml`). **Nunca** uses credenciales así en producción.

## 1. Crea dos backups: uno normal y uno blindado (5 min)

El experimento controlado: el **mismo** dato, en dos buckets, con una sola
diferencia — el candado.

```bash
# Bucket NORMAL (como cualquier backup S3 sin proteger)
mc mb local/backup-normal

# BÓVEDA: bucket con Object Lock, retencion COMPLIANCE de 30 dias
mc mb --with-lock local/boveda
mc retention set --default COMPLIANCE 30d local/boveda
```

Sube el "backup de anoche" a ambos:

```bash
tar czf /tmp/backup.tar.gz datasets/caso4/produccion
mc cp /tmp/backup.tar.gz local/backup-normal/
mc cp /tmp/backup.tar.gz local/boveda/

mc ls local/boveda                          # deberia listar backup.tar.gz
mc retention info local/boveda/backup.tar.gz # Mode: COMPLIANCE, expiring in 29 days
```

**Pregunta de diseño (antes de atacar):** ¿por qué COMPLIANCE y no GOVERNANCE?
GOVERNANCE deja que un rol privilegiado levante el candado — una llave más que
el atacante puede robar. COMPLIANCE **no lo levanta nadie** (ni root, ni el
proveedor) hasta que expira. Para una bóveda anti-ransomware, esa es la elección.

## 2. Ataca ambos con tus credenciales válidas (10 min)

Esto es lo que hace el ransomware moderno: no rompe criptografía, **usa las
llaves que ya robó**. El script `atacar_boveda.sh` intenta borrar y sobrescribir.

```bash
# Primero el bucket normal
scripts/atacar_boveda.sh local/backup-normal
```

Verás `[DESTRUIDO] EL BACKUP SE PERDIO`. Sin inmutabilidad, credenciales válidas
= backup borrado. Ahora la bóveda:

```bash
scripts/atacar_boveda.sh local/boveda
```

Verás `[RESISTIO] LA BOVEDA SOBREVIVIO`. El mismo comando, el mismo atacante,
dos finales.

## 3. El matiz que separa a un junior de un senior (10 min)

Corre el borrado "a mano" sobre la bóveda y **lee con atención**:

```bash
mc rm --recursive --force local/boveda
mc ls local/boveda                    # ¡se ve VACÍO! ¿se perdió?
mc ls --versions local/boveda         # NO: aquí está la verdad
```

Con Object Lock el bucket tiene **versionado**. Tu `rm` no borró nada: solo
añadió un **delete marker** encima. La versión bloqueada (`PUT`) sigue intacta
debajo. Compáralo con el bucket normal:

```bash
mc ls --versions local/backup-normal  # vacío de verdad — ahí no hay nada que recuperar
```

Ahora intenta destruir la versión bloqueada **a propósito**, con su version-id:

```bash
VID=$(mc ls --versions --json local/boveda | \
      python3 -c "import json,sys
for l in sys.stdin:
    o=json.loads(l)
    if not o.get('isDeleteMarker') and o.get('size',0)>0: print(o['versionId']); break")

mc rm --version-id "$VID" --force local/boveda/backup.tar.gz
```

Respuesta del servidor:

```
mc: <ERROR> ... Object ... is WORM protected and cannot be overwritten
```

**Ni siquiera tú, con las llaves maestras, puedes destruirla.** Eso es WORM.

## 4. Recupera desde la bóveda

Quitar el delete marker "resucita" el objeto (o restauras directo por version-id):

```bash
mc cat --version-id "$VID" local/boveda/backup.tar.gz > /tmp/recuperado.tar.gz
tar tzf /tmp/recuperado.tar.gz | head        # el backup intacto, listo para restaurar
```

> ✅ **Checkpoint Parte 1:** el bucket normal se perdió ante el mismo ataque que
> la bóveda resistió; entiendes por qué COMPLIANCE > GOVERNANCE y por qué el
> `rm` en un bucket con lock es reversible. Sigue la Parte 2: proteger el
> **repositorio de backup** (restic) cuando el candado no está en cada objeto
> sino en el **servidor**.
