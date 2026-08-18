#!/usr/bin/env python3
"""Genera el dataset sintético de la Sesión 4 (bóveda inmutable).

Crea datasets/caso4/produccion/ con archivos "de negocio" que vas a respaldar,
más un manifiesto de hashes (SHA-256) que sirve para la verificación de la
Parte 3 (mismo principio de scoring de integridad de la Sesión 2).

100% sintético. Determinista (semilla fija). Sin dependencias: solo stdlib.
"""
import hashlib
import json
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "datasets" / "caso4"
PROD = BASE / "produccion"

rng = random.Random(92)

# Documentos "de negocio" que la organización respalda cada noche.
ARCHIVOS = {
    "contabilidad/balance_2025Q1.csv": (
        "cuenta,debe,haber\n"
        "caja,1200000,0\n"
        "bancos,8400000,0\n"
        "clientes,3100000,0\n"
        "proveedores,0,2750000\n"
    ),
    "contabilidad/nomina_abril.csv": (
        "empleado,cargo,salario\n"
        "a.perez,analista,4200000\n"
        "l.rojas,auxiliar,2600000\n"
        "c.gomez,desarrollador,5800000\n"
    ),
    "legal/contrato_marco_proveedor.txt": (
        "CONTRATO MARCO DE PRESTACION DE SERVICIOS\n"
        "Entre la Empresa y el Proveedor, por 12 meses, prorrogables.\n"
        "Clausula de confidencialidad y niveles de servicio (SLA) anexos.\n"
    ),
    "ti/inventario_servidores.json": json.dumps({
        "servidores": [
            {"host": "SRV-APP-01", "rol": "aplicaciones", "critico": True},
            {"host": "SRV-DB-01", "rol": "base de datos", "critico": True},
            {"host": "SRV-BACKUP", "rol": "backup", "critico": True},
        ]
    }, ensure_ascii=False, indent=2) + "\n",
    "ti/runbook_recuperacion.md": (
        "# Runbook de recuperacion (borrador)\n"
        "1. Aislar el equipo afectado de la red.\n"
        "2. Identificar la ultima copia limpia en la boveda inmutable.\n"
        "3. Verificar integridad (hashes) antes de restaurar.\n"
        "4. Restaurar en entorno limpio y validar.\n"
    ),
}


def cuerpo_binario(nombre: str, kb: int) -> bytes:
    r = random.Random(hash(nombre) & 0xFFFF)
    return bytes(r.randrange(256) for _ in range(kb * 1024))


def generar() -> None:
    if PROD.exists():
        for p in sorted(PROD.rglob("*"), reverse=True):
            p.unlink() if p.is_file() else p.rmdir()
    PROD.mkdir(parents=True, exist_ok=True)

    manifiesto = {}
    for rel, contenido in ARCHIVOS.items():
        f = PROD / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(contenido, encoding="utf-8")
        manifiesto[rel] = hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    # Un par de "adjuntos" binarios para que el backup tenga volumen realista.
    for rel, kb in [("adjuntos/escaneo_factura.bin", 64),
                    ("adjuntos/base_datos_export.bin", 128)]:
        f = PROD / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        datos = cuerpo_binario(rel, kb)
        f.write_bytes(datos)
        manifiesto[rel] = hashlib.sha256(datos).hexdigest()

    (BASE / "manifiesto_sha256.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(1 for _ in PROD.rglob("*") if _.is_file())
    print(f"[ok] {PROD}  ({total} archivos de produccion)")
    print(f"[ok] {BASE / 'manifiesto_sha256.json'}  ({len(manifiesto)} hashes)")
    print("Dataset sintetico del caso 4 listo. Nada aqui es sensible ni real.")


if __name__ == "__main__":
    generar()
