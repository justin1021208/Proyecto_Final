"""Lectura y escritura de archivos JSON dentro de la carpeta Datos."""
import json
from pathlib import Path

DATOS = Path(__file__).resolve().parent.parent / "Datos"


def leer(nombre, por_defecto):
    try:
        with open(DATOS / nombre, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return por_defecto


def guardar(nombre, datos):
    DATOS.mkdir(exist_ok=True)
    with open(DATOS / nombre, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
