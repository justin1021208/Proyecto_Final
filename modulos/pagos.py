"""Registro de pagos. Cada pago extiende la membresía del cliente."""
from datetime import date, timedelta

from modulos import almacen, membresias, pila_historial

ARCHIVO = "pagos.json"
METODOS = ["Efectivo", "Transferencia", "Tarjeta"]


def obtener_pagos():
    datos = almacen.leer(ARCHIVO, [])
    return [p for p in datos if isinstance(p, dict)]


def ultimos_pagos(cantidad=15):
    return list(reversed(obtener_pagos()))[:cantidad]


def _monto(pago):
    try:
        return float(pago.get("monto") or 0)
    except (TypeError, ValueError):
        return 0.0


def ingresos_del_mes():
    mes = date.today().strftime("%Y-%m")
    return sum(_monto(p) for p in obtener_pagos() if str(p.get("fecha", "")).startswith(mes))


def registrar_pago(cliente, plan_id, metodo):
    """Guarda el pago y devuelve (se_guardó, mensaje)."""
    plan = membresias.PLANES.get(plan_id)
    if not cliente:
        return False, "Elige un cliente."
    if not plan:
        return False, "Elige un plan."
    if metodo not in METODOS:
        return False, "Elige un método de pago."

    pagos = obtener_pagos()
    hoy = date.today()

    # Si la membresía sigue activa, el nuevo plan empieza al día siguiente de su vencimiento.
    actual = membresias.estado_de(cliente, pagos, hoy)
    inicio = actual["vence"] + timedelta(days=1) if actual["estado"] == "activa" else hoy
    vence = inicio + timedelta(days=plan["dias"] - 1)

    pagos.append({
        "cliente": cliente,
        "plan_id": plan_id,
        "plan": plan["nombre"],
        "monto": plan["precio"],
        "metodo": metodo,
        "fecha": hoy.isoformat(),
        "vence": vence.isoformat(),
    })
    almacen.guardar(ARCHIVO, pagos)
    pila_historial.apilar("pago", f"{cliente} pagó {plan['nombre']} (C$ {plan['precio']:,})")

    return True, f"Pago registrado. {cliente} queda activo hasta el {vence:%d/%m/%Y}."
