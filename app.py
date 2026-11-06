
from flask import Flask, render_template, request
from modulos.clientes import obtener_clientes, agregar_cliente

app = Flask(__name__)


@app.route("/")
def inicio():
    lista = obtener_clientes()
    return render_template("index.html", clientes=lista)


@app.route("/clientes", methods=["POST"])
def clientes():
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()

    mensaje = agregar_cliente(nombre, telefono)
    lista = obtener_clientes()

    return render_template(
        "index.html",
        clientes=lista,
        mensaje=mensaje,
        seccion="clientes"
    )


if __name__ == "__main__":
    app.run(debug=True)
