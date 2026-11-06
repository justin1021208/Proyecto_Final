import json

Archivo = "datos/clientes.json"

def obtener_clientes():
    with open(Archivo, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def agregar_cliente(nombre, telefono):
    clientes = obtener_clientes()

    if not nombre or not telefono:
        return "Debes completar todos los campos."

    for cliente in clientes:
        if cliente["telefono"] == telefono:
            return "Este teléfono ya está registrado."

    nuevo = {
        "id": len(clientes) + 1,
        "nombre": nombre,
        "telefono": telefono,
        "membresia": "Inactiva"
    }

    clientes.append(nuevo)

    with open(Archivo, "w", encoding="utf-8") as archivo:
        json.dump(clientes, archivo, indent=4, ensure_ascii=False)

    return "Cliente registrado correctamente."
