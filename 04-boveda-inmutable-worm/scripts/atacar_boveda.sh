#!/usr/bin/env bash
# =====================================================================
#  atacar_boveda.sh — el "ransomware" del lab (Sesión 4, 92-EAN)
#
#  Simula lo que hace un atacante que YA robó credenciales validas de
#  administrador: intenta DESTRUIR el backup (borrar objetos, sobrescribir).
#  No es malware: es una secuencia de comandos 'mc' con TUS credenciales.
#  Si la boveda resiste esto, resiste al real.
#
#  El veredicto se decide por las VERSIONES que sobreviven, no por 'mc ls':
#  en un bucket con Object Lock, 'rm' solo añade un delete-marker y la
#  version bloqueada (PUT) sigue debajo. Contar bien es parte de la leccion.
#
#  Uso:
#    scripts/atacar_boveda.sh <alias/bucket>
#  Ejemplos:
#    scripts/atacar_boveda.sh local/boveda          # boveda WORM  -> debe RESISTIR
#    scripts/atacar_boveda.sh local/backup-normal   # sin lock     -> se PIERDE
# =====================================================================
set -uo pipefail

OBJETIVO="${1:-}"
if [ -z "$OBJETIVO" ]; then
  echo "uso: $0 <alias/bucket>   (ej: local/boveda)" >&2
  exit 2
fi

R="\033[0;31m"; G="\033[0;32m"; Y="\033[0;33m"; B="\033[0;34m"; N="\033[0m"
paso(){ echo -e "\n${B}==>${N} $1"; }
ok(){   echo -e "${G}[RESISTIO]${N} $1"; }
bad(){  echo -e "${R}[DESTRUIDO]${N} $1"; }

# Cuenta versiones PUT vivas (no delete-markers): lo que realmente se puede
# recuperar. Robusto aunque 'mc ls' de superficie se vea vacio.
contar_datos_vivos(){
  mc ls --versions --json "$1" 2>/dev/null | python3 -c "
import json,sys
n=0
for l in sys.stdin:
    try: o=json.loads(l)
    except Exception: continue
    if not o.get('isDeleteMarker') and o.get('size',0)>0: n+=1
print(n)"
}

echo -e "${Y}############################################################${N}"
echo -e "${Y}#  SIMULACRO DE ATAQUE A LA BOVEDA — objetivo: ${OBJETIVO}${N}"
echo -e "${Y}#  (usando credenciales validas, como el ransomware real)${N}"
echo -e "${Y}############################################################${N}"

paso "1/3 · Datos recuperables antes del ataque"
ANTES=$(contar_datos_vivos "$OBJETIVO")
echo "    versiones de datos vivas: $ANTES"

paso "2/3 · Intento de BORRADO masivo (rm --recursive --force)"
SALIDA=$(mc rm --recursive --force "$OBJETIVO" 2>&1)
echo "$SALIDA" | sed 's/^/    /'
if echo "$SALIDA" | grep -qiE "WORM|denied|retention"; then
  ok "el borrado fue DENEGADO explicitamente por la proteccion WORM"
elif echo "$SALIDA" | grep -qi "delete marker"; then
  echo "    (con Object Lock, 'rm' solo crea delete-markers: la version sigue debajo)"
else
  echo "    (el objeto se borro sin dejar version recuperable)"
fi

paso "3/3 · Intento de DESTRUIR permanentemente la version mas reciente"
# Nota: algunos clientes 'mc' con --force silencian el error WORM. Por eso NO
# confiamos en el mensaje: comprobamos si la version SIGUE existiendo despues.
VID=$(mc ls --versions --json "$OBJETIVO" 2>/dev/null | python3 -c "
import json,sys
for l in sys.stdin:
    try: o=json.loads(l)
    except Exception: continue
    if not o.get('isDeleteMarker') and o.get('size',0)>0:
        print(o['versionId'], o['key']); break")
if [ -n "$VID" ]; then
  set -- $VID
  SALIDA=$(mc rm --version-id "$1" --force "$OBJETIVO/$2" 2>&1)
  [ -n "$SALIDA" ] && echo "$SALIDA" | sed 's/^/    /'
  if mc stat --version-id "$1" "$OBJETIVO/$2" >/dev/null 2>&1; then
    ok "la version sigue existiendo: la destruccion fue BLOQUEADA por WORM"
  else
    bad "la version se destruyo permanentemente (sin proteccion WORM)"
  fi
else
  echo "    no quedan versiones vivas que destruir"
fi

paso "Veredicto · Datos recuperables despues del ataque"
DESPUES=$(contar_datos_vivos "$OBJETIVO")
echo "    versiones vivas antes:   $ANTES"
echo "    versiones vivas despues: $DESPUES"
if [ "$ANTES" -gt 0 ] && [ "$DESPUES" -ge "$ANTES" ]; then
  echo -e "\n${G}================================================${N}"
  ok "LA BOVEDA SOBREVIVIO. La copia limpia sigue recuperable."
  echo -e "${G}================================================${N}"
  exit 0
else
  echo -e "\n${R}================================================${N}"
  bad "EL BACKUP SE PERDIO ($ANTES -> $DESPUES versiones vivas)."
  echo -e "${R}  Sin inmutabilidad, las credenciales robadas bastan.${N}"
  echo -e "${R}================================================${N}"
  exit 1
fi
