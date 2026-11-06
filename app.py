from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from modulos import membresias, pagos, pila_historial
from modulos.clientes import agregar_cliente, obtener_clientes

app = Flask(__name__)
app.secret_key = "gymcontrol-clave-local"  # necesaria para flash()

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ---------- Filtros para las plantillas ----------

@app.template_filter("cordobas")
def cordobas(valor):
    try:
        return f"C$ {float(valor):,.0f}"
    except (TypeError, ValueError):
        return "C$ 0"


@app.template_filter("fecha")
def fecha(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor or ""


# ---------- Ayudas ----------

def _campo(cliente, campo):
    """Lee un dato del cliente sin importar si es diccionario u objeto."""
    if isinstance(cliente, dict):
        return cliente.get(campo, "")
    return getattr(cliente, campo, "")


def nombres_clientes():
    return [_campo(c, "nombre") for c in obtener_clientes()]


def clientes_con_estado():
    lista_pagos = pagos.obtener_pagos()
    return [
        {
            "nombre": _campo(c, "nombre"),
            "telefono": _campo(c, "telefono"),
            "membresia": membresias.estado_de(_campo(c, "nombre"), lista_pagos),
        }
        for c in obtener_clientes()
    ]


def _mensaje(texto, por_defecto):
    return texto if isinstance(texto, str) and texto else por_defecto


# ---------- Rutas ----------

@app.route("/", endpoint="inicio")
def vista_inicio():
    hoy = date.today()
    hora = datetime.now().hour
    saludo = "Buenos días" if hora < 12 else "Buenas tardes" if hora < 19 else "Buenas noches"

    lista = clientes_con_estado()
    activas = [c for c in lista if c["membresia"]["estado"] == "activa"]
    por_vencer = sorted(
        (c for c in activas if c["membresia"]["dias"] <= 7),
        key=lambda c: c["membresia"]["dias"],
    )

    return render_template(
        "inicio.html",
        saludo=saludo,
        fecha_larga=f"{DIAS[hoy.weekday()]} {hoy.day} de {MESES[hoy.month - 1]}",
        total=len(lista),
        activas=len(activas),
        por_vencer=por_vencer,
        ingresos=pagos.ingresos_del_mes(),
        movimientos=pila_historial.ver(5),
    )


@app.route("/clientes", methods=["GET", "POST"], endpoint="clientes")
def vista_clientes():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()

        antes = len(obtener_clientes())
        respuesta = agregar_cliente(nombre, telefono)

        if len(obtener_clientes()) > antes:
            pila_historial.apilar("cliente", f"Nuevo cliente: {nombre}")
            flash(_mensaje(respuesta, "Cliente guardado."), "ok")
        else:
            flash(_mensaje(respuesta, "No se pudo guardar el cliente."), "error")

        # Redirigir evita que F5 vuelva a enviar el formulario y duplique al cliente.
        return redirect(url_for("clientes"))

    return render_template("clientes.html", clientes=clientes_con_estado())


@app.route("/pagos", methods=["GET", "POST"], endpoint="pagos")
def vista_pagos():
    if request.method == "POST":
        cliente = request.form.get("cliente", "").strip()
        if cliente not in nombres_clientes():
            flash("Elige un cliente de la lista.", "error")
        else:
            guardado, mensaje = pagos.registrar_pago(
                cliente,
                request.form.get("plan", ""),
                request.form.get("metodo", ""),
            )
            flash(mensaje, "ok" if guardado else "error")
        return redirect(url_for("pagos"))

    return render_template(
        "pagos.html",
        clientes=nombres_clientes(),
        planes=membresias.PLANES,
        metodos=pagos.METODOS,
        recientes=pagos.ultimos_pagos(15),
        cliente_sel=request.args.get("cliente", ""),
        plan_sel=request.args.get("plan", ""),
    )


@app.route("/membresias", endpoint="membresias")
def vista_membresias():
    orden = {"activa": 0, "vencida": 1, "sin": 2}
    estados = sorted(
        clientes_con_estado(),
        key=lambda c: (orden[c["membresia"]["estado"]], c["membresia"]["dias"] or 0),
    )
    return render_template("membresias.html", planes=membresias.PLANES, estados=estados)


@app.route("/historial", endpoint="historial")
def vista_historial():
    return render_template("historial.html", movimientos=pila_historial.ver(100))


if __name__ == "__main__":
    app.run(debug=True)