# Parte 3 · Vigilar la bóveda (FIM) y restaurar con confianza

**Taller Sesión 4 · Ciber-Recuperación (92-EAN)** · Duración: 25 min

> Ya tienes copias que resisten el borrado. Falta la **cámara de seguridad**:
> saber si alguien tocó (o intentó tocar) la carpeta del backup, y —cuando
> restaures— comprobar que lo recuperado es **bit a bit** lo original. Eso cierra
> el "0" de la regla 3-2-1-1-0: **cero errores al verificar**.

## 1. AIDE: el inventario notariado (10 min)

**AIDE** (Advanced Intrusion Detection Environment) guarda una base de datos de
hashes de los archivos críticos y avisa de cualquier cambio. Es tu scoring de
integridad de la Sesión 2, corriendo como vigilante permanente.

```bash
# Ubuntu:  sudo apt install -y aide
# macOS:   brew install aide   (o usa el fallback en Python de la seccion 3)
```

Los datos del lab viven en `./data` (volúmenes de MinIO y restic montados al
host). Vamos a vigilar esa carpeta. Crea una config mínima:

```bash
cat > /tmp/aide.conf <<'EOF'
database=file:/tmp/aide.db
database_out=file:/tmp/aide.db.new
gzip_dbout=no
Todos = p+i+n+u+g+s+sha256
./data Todos
EOF

sudo aide -c /tmp/aide.conf --init          # notaría inicial (crea la base)
sudo mv /tmp/aide.db.new /tmp/aide.db       # promueve la base recien creada
```

> La base de datos de AIDE (`aide.db`) es tan valiosa como el backup: guárdala
> **en la bóveda** (Parte 1). Si el atacante puede reescribir la notaría, el FIM
> no vale nada.

## 2. Simula la manipulación y detéctala (10 min)

Un atacante toca la carpeta de backup — añade un archivo y modifica otro:

```bash
echo "carga_util_ransomware" | tee data/minio/nota_atacante.txt >/dev/null
# (si tienes un objeto extraible, modifícalo; si no, basta el archivo nuevo)

sudo aide -c /tmp/aide.conf --check
```

AIDE reporta el cambio:

```
Added entries:
  f++++++++++++++++: /.../data/minio/nota_atacante.txt
AIDE found differences between database and filesystem!!
```

Ahí tienes la alerta: **algo cambió en la bóveda que tú no autorizaste**. En
producción, esto es lo que **Wazuh FIM** hace en tiempo real y escala a cientos
de hosts (mismo concepto, agente que vigila `syscheck` y alerta al SIEM). AIDE
es la versión que ves "por dentro" en un solo host.

> **Sin AIDE instalado (fallback):** el script `verificar_integridad.py` aplica
> la misma lógica de hashes sobre una carpeta contra el manifiesto del dataset.

## 3. Restaura desde la bóveda y verifica el "0" (5 min)

La detección disparó → ahora recuperas desde la copia inmutable de la Parte 1 (o
el repo append-only de la Parte 2) y **compruebas la integridad**:

```bash
# recupera (ejemplo con restic de la Parte 2)
export RESTIC_REPOSITORY="rest:http://localhost:8000/" RESTIC_PASSWORD="lab123"
SNAP=$(restic snapshots --json | python3 -c "import json,sys;print(json.load(sys.stdin)[-1]['short_id'])")
restic restore "$SNAP" --target /tmp/recuperado

# verifica bit a bit contra el manifiesto SHA-256 (scoring de la Sesion 2)
python3 scripts/verificar_integridad.py /tmp/recuperado/prod
```

Salida esperada:

```
7/7 intactos · 0 alterados · 0 faltantes
RESULTADO: restauracion 100% integra. Cero errores de verificacion.
```

Ese `0 alterados · 0 faltantes` es el **"0" de 3-2-1-1-0**: un backup no está
probado hasta que restauras y verificas. Una copia sin esta prueba es una
promesa, no un respaldo.

## 4. Cierre de la sesión y del ciclo técnico

El arsenal completo que te llevas:

```
Deteccion (S3)  →  la regla dispara: "borraron las shadow copies"
      │
      ▼
Boveda WORM (Parte 1)     el backup EXISTE y no se puede destruir
Append-only (Parte 2)     el cliente comprometido no poda la historia
FIM / AIDE (Parte 3)      sabes que alguien toco la boveda
Verificacion (S2)         restauras y confirmas: 0 errores  ──►  no pagas rescate
```

- **Object Lock / append-only** aportan **inmutabilidad** (la copia sobrevive).
- **AIDE / Wazuh** aportan **visibilidad** (te enteras del intento).
- **La verificación de hashes** aporta **confianza** (lo restaurado es correcto).

Sin las tres, la recuperación es un acto de fe. Esta es la base de la Sesión 5:
cuando todo esto dispara a las 3 a.m., un **copiloto RAG local** te guía por el
runbook — sin sacar tus procedimientos de la sala.

> ✅ **Checkpoint Parte 3:** AIDE detectó la manipulación de la carpeta de
> backup, restauraste desde la bóveda y `verificar_integridad.py` confirmó
> `0 alterados · 0 faltantes`. Cerraste la regla 3-2-1-1-0 de punta a punta.

## Limpieza

```bash
docker compose down            # detiene MinIO y rest-server (conserva ./data)
docker compose down -v         # ...y borra tambien los volumenes del lab
```
