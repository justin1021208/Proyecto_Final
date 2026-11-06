"""Historial de movimientos como una pila (LIFO): lo último en entrar es lo primero que se ve."""
from datetime import datetime

from modulos import almacen

ARCHIVO = "historial.json"
LIMITE = 300


def apilar(tipo, detalle):
    pila = almacen.leer(ARCHIVO, [])
    pila.append({
        "tipo": tipo,
        "detalle": detalle,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    almacen.guardar(ARCHIVO, pila[-LIMITE:])


def ver(limite=None):
    """Movimientos del más reciente al más antiguo."""
    pila = almacen.leer(ARCHIVO, [])
    return list(reversed(pila))[:limite]
