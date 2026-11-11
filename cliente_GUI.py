# ---------------------------------------------------------
# MENÚ DE CLIENTES (parte de quien hace Cliente)
# ---------------------------------------------------------
from cliente import Cliente
from cliente_dao import ClienteDAO

dao = ClienteDAO()


def alta():
    tipo = input("Tipo de documento (DNI/LC/LE/CI/PAS): ").strip().upper()
    nro = input("Número de documento: ").strip()
    nombre = input("Nombre: ").strip().title()
    apellido = input("Apellido: ").strip().title()

    nuevo = Cliente(tipo, nro, nombre, apellido)

    error = nuevo.validar()
    if error:
        print("Error:", error)
        return

    existente = dao.buscar_por_documento(tipo, nro)
    if existente:
        if existente.estado == "Activo":
            print("Error: ya existe un cliente con ese documento.")
        else:
            print(f"Error: ese cliente está dado de baja (Nro Doc {existente.nro_dni})")
        return

    dao.agregar(nuevo)
    print("Cliente creado:", nuevo)


def listar():
    incluir = input("¿Incluir inactivos? (s/n): ").strip().lower() == "s"
    clientes = dao.listar(incluir)
    if len(clientes) == 0:
        print("No hay clientes.")
    for c in clientes:
        print(c)


def buscar():
    tipo = input("Tipo de documento: ").strip().upper()
    nro = input("Número de documento: ").strip()
    cliente = dao.buscar_por_documento(tipo, nro)
    if cliente is None:
        print("No existe un cliente con ese documento.")
    else:
        print(cliente)


def pedir_tipo_dni():
    texto = input("Tipo Documento del cliente: ").strip()
    print(repr(texto))
    if texto not in ("DNI", "LC", "LE", "CI", "PAS"):
        print('Error: el Documento debe ser "DNI", "LC", "LE", "CI", "PAS"')
        return None
    return texto

def pedir_documento():
    texto = input("Documento del cliente: ").strip()
    if not texto.isdigit():
        print("Error: el Documento debe ser un número.")
        return None
    return int(texto)


def modificar():
    tipo_dni = pedir_tipo_dni()
    nro_dni = pedir_documento()
    if nro_dni is None:
        return
    cliente = dao.buscar_por_documento(tipo_dni, nro_dni)
    if cliente is None:
        print("No existe un cliente con ese documento.")
        return
    if cliente.estado == "Inactivo":
        print("Error: no se puede modificar un cliente dado de baja.")
        return

    print("Actual:", cliente, "(Enter para dejar el valor como está)")
    tipo = input(f"Tipo de documento [{cliente.tipo_dni}]: ").strip().upper() or cliente.tipo_dni
    nro = input(f"Número de documento [{cliente.nro_dni}]: ").strip() or cliente.nro_dni
    nombre = input(f"Nombre [{cliente.nombre}]: ").strip().title() or cliente.nombre
    apellido = input(f"Apellido [{cliente.apellido}]: ").strip().title() or cliente.apellido

    modificado = Cliente(tipo, nro, nombre, apellido, cliente.estado)

    error = modificado.validar()
    if error:
        print("Error:", error)
        return

    otro = dao.buscar_por_documento(tipo, nro)
    if otro and otro.nro_dni != cliente.nro_dni:
        print("Error: otro cliente ya tiene ese documento.")
        return

    dao.modificar(modificado)
    print("Cliente actualizado:", modificado)


def baja():
    tipo_dni = pedir_tipo_dni()
    nro_dni = pedir_documento()
    if nro_dni is None:
        return
    cliente = dao.buscar_por_documento(tipo_dni, nro_dni)
    if cliente is None:
        print("No existe un cliente con ese documento.")
        return
    if cliente.estado == "Inactivo":
        print("El cliente ya estaba dado de baja.")
        return

    # TODO (cuando esté Mascota): no permitir la baja si tiene mascotas activas.

    cliente.estado = "Inactivo"     # no se borra, solo cambia el estado
    dao.modificar(cliente)
    print("Baja realizada:", cliente)


def menu_clientes():
    opciones = {"1": alta, "2": listar, "3": buscar, "4": modificar, "5": baja}
    while True:
        print("\n=== ABM CLIENTES ===")
        print("1. Alta")
        print("2. Listar")
        print("3. Buscar por documento")
        print("4. Modificar")
        print("5. Baja")
        print("0. Volver")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            break
        elif opcion in opciones:
            opciones[opcion]()
        else:
            print("Opción inválida.")

menu_clientes()