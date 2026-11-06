"""Planes de membresía y cálculo del estado de cada cliente.

Los precios son de ejemplo: cámbialos aquí y toda la app se actualiza.
"""
from datetime import date, datetime

PLANES = {
    "diario":     {"nombre": "Pase diario", "dias": 1,  "precio": 60,   "detalle": "Acceso solo por hoy"},
    "semanal":    {"nombre": "Semanal",     "dias": 7,  "precio": 300,  "detalle": "7 días seguidos de acceso"},
    "mensual":    {"nombre": "Mensual",     "dias": 30, "precio": 900,  "detalle": "30 días seguidos de acceso"},
    "trimestral": {"nombre": "Trimestral",  "dias": 90, "precio": 2400, "detalle": "90 días seguidos de acceso"},
}


def _fecha(texto):
    return datetime.strptime(texto, "%Y-%m-%d").date()


def _resultado(estado, plan, vence, dias, etiqueta, clase):
    return {"estado": estado, "plan": plan, "vence": vence, "dias": dias,
            "etiqueta": etiqueta, "clase": clase}


def estado_de(cliente, lista_pagos, hoy=None):
    """Devuelve el estado de la membresía de un cliente según sus pagos."""
    hoy = hoy or date.today()
    nombre = cliente.strip().lower()

    vencimientos = []
    for p in lista_pagos:
        if str(p.get("cliente", "")).strip().lower() != nombre:
            continue
        try:
            vencimientos.append((_fecha(p["vence"]), p.get("plan", "")))
        except (KeyError, ValueError, TypeError):
            continue

    if not vencimientos:
        return _resultado("sin", "", None, None, "Sin membresía", "badge-none")

    vence, plan = max(vencimientos)
    dias = (vence - hoy).days

    if dias < 0:
        return _resultado("vencida", plan, vence, dias, f"Venció el {vence:%d/%m}", "badge-off")
    if dias == 0:
        return _resultado("activa", plan, vence, dias, "Vence hoy", "badge-warn")
    if dias <= 7:
        texto = "1 día" if dias == 1 else f"{dias} días"
        return _resultado("activa", plan, vence, dias, f"Vence en {texto}", "badge-warn")
    return _resultado("activa", plan, vence, dias, f"Activa hasta {vence:%d/%m}", "badge-ok")
