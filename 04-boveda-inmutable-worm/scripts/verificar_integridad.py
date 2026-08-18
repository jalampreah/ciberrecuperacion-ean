#!/usr/bin/env python3
"""Verifica la integridad de una carpeta restaurada contra el manifiesto SHA-256.

Es el puente con la Sesión 2 (scoring de integridad): tras restaurar desde la
bóveda, no basta con que los archivos existan — deben ser BIT A BIT los mismos.
Ese es el "0" de la regla 3-2-1-1-0 (cero errores al verificar).

Uso:
    python3 scripts/verificar_integridad.py <carpeta_restaurada> [manifiesto.json]

Sin dependencias: solo stdlib. Código de salida 0 si todo cuadra, 1 si no.
"""
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "datasets" / "caso4"


def sha256_archivo(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(f"uso: {sys.argv[0]} <carpeta_restaurada> [manifiesto.json]")
    carpeta = Path(sys.argv[1])
    manif_path = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE / "manifiesto_sha256.json"
    if not carpeta.is_dir():
        raise SystemExit(f"no existe la carpeta: {carpeta}")
    manifiesto = json.loads(manif_path.read_text(encoding="utf-8"))

    ok, cambiados, faltantes = [], [], []
    for rel, esperado in sorted(manifiesto.items()):
        f = carpeta / rel
        if not f.is_file():
            faltantes.append(rel)
            continue
        real = sha256_archivo(f)
        (ok if real == esperado else cambiados).append(rel)

    print(f"{'archivo':<40} estado")
    print("-" * 58)
    for rel in sorted(manifiesto):
        if rel in ok:
            estado = "OK"
        elif rel in cambiados:
            estado = "** ALTERADO **"
        else:
            estado = "** FALTANTE **"
        print(f"{rel:<40} {estado}")

    total = len(manifiesto)
    print("-" * 58)
    print(f"{len(ok)}/{total} intactos · {len(cambiados)} alterados · {len(faltantes)} faltantes")
    if cambiados or faltantes:
        print("\nRESULTADO: la restauracion NO es integra (regla 3-2-1-1-0: el '0' falla).")
        sys.exit(1)
    print("\nRESULTADO: restauracion 100% integra. Cero errores de verificacion.")
    sys.exit(0)


if __name__ == "__main__":
    main()
