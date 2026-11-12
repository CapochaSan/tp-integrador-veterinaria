from cliente import Cliente
from cliente_dao import ClienteDAO
import flet as ft

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
            return
        # Estaba dado de baja: se lo da de alta de nuevo con los datos recién cargados
        dao.modificar(nuevo)
        print("Cliente dado de alta nuevamente:", nuevo)
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
    texto = input("Tipo Documento del cliente: ").strip().upper()
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
    if tipo_dni is None:
        return
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

    # El documento no se modifica (es lo que identifica al cliente): solo nombre y apellido
    print("Actual:", cliente, "(Enter para dejar el valor como está)")
    nombre = input(f"Nombre [{cliente.nombre}]: ").strip().title() or cliente.nombre
    apellido = input(f"Apellido [{cliente.apellido}]: ").strip().title() or cliente.apellido

    modificado = Cliente(cliente.tipo_dni, cliente.nro_dni, nombre, apellido, cliente.estado)

    error = modificado.validar()
    if error:
        print("Error:", error)
        return

    dao.modificar(modificado)
    print("Cliente actualizado:", modificado)


def baja():
    tipo_dni = pedir_tipo_dni()
    if tipo_dni is None:
        return
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


# =========================================================
# PANTALLA (Flet)
# =========================================================
NUEVO_FLET = hasattr(ft, "run")     # las versiones nuevas de Flet tienen ft.run


# En Flet 1.0 ElevatedButton se eliminó y pasó a llamarse Button.
# Estas líneas eligen el que exista en tu versión.
BOTON = getattr(ft, "Button", None) or ft.ElevatedButton
BOTON_BORDE = getattr(ft, "OutlinedButton", BOTON)
BOTON_TEXTO = getattr(ft, "TextButton", BOTON)


def boton(texto, accion, clase=None):
    """Crea un botón con texto. El nombre del parámetro cambió entre versiones de Flet."""
    clase = clase or BOTON
    if NUEVO_FLET:
        return clase(content=texto, on_click=accion)
    return clase(text=texto, on_click=accion)


def pantallaCliente(page: ft.Page):
    page.title = "Gestión de Clientes"
    page.scroll = ft.ScrollMode.AUTO

    # documento del cliente que se está editando (None = ninguno)
    seleccionado = {"tipo": None, "nro": None}

    # ---------- CAMPOS Y TABLA ----------
    tipo = ft.Dropdown(
        label="Tipo de documento", width=200, value="DNI",
        options=[ft.dropdown.Option(t) for t in ("DNI", "LC", "LE", "CI", "PAS")],
    )
    nro = ft.TextField(label="Número de documento", width=200)
    nombre = ft.TextField(label="Nombre", width=200)
    apellido = ft.TextField(label="Apellido", width=200)
    mostrar_inactivos = ft.Checkbox(label="Mostrar inactivos", value=False,
                                    on_change=lambda e: refrescar())
    mensaje = ft.Text("")           # acá aparecen los avisos y errores
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Documento")),
            ft.DataColumn(label=ft.Text("Apellido")),
            ft.DataColumn(label=ft.Text("Nombre")),
            ft.DataColumn(label=ft.Text("Estado")),
            ft.DataColumn(label=ft.Text("")),
        ],
        rows=[],
    )

    # ---------- FUNCIONES AUXILIARES ----------
    def avisar(texto, ok=True):
        mensaje.value = texto
        mensaje.color = ft.Colors.GREEN if ok else ft.Colors.RED
        page.update()

    def limpiar():
        seleccionado["tipo"] = None
        seleccionado["nro"] = None
        tipo.value = "DNI"
        nro.value = ""
        nombre.value = ""
        apellido.value = ""
        tipo.disabled = False       # el documento se puede escribir de nuevo
        nro.disabled = False

    def cargar_tabla():
        """Vuelve a llenar la tabla con los clientes de la base."""
        tabla.rows = []
        for c in dao.listar(mostrar_inactivos.value) or []:
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(content=ft.Text(f"{c.tipo_dni} {c.nro_dni}")),
                ft.DataCell(content=ft.Text(c.apellido)),
                ft.DataCell(content=ft.Text(c.nombre)),
                ft.DataCell(content=ft.Text(c.estado)),
                ft.DataCell(content=boton(
                    "Editar",
                    lambda _event, t=c.tipo_dni, n=c.nro_dni: seleccionar(t, n),
                    BOTON_TEXTO)),
            ]))

    def refrescar():
        cargar_tabla()
        page.update()

    def seleccionar(tipo_dni, nro_dni):
        """Al apretar 'Editar' en una fila, pasa los datos al formulario."""
        c = dao.buscar_por_documento(tipo_dni, nro_dni)
        seleccionado["tipo"] = c.tipo_dni
        seleccionado["nro"] = c.nro_dni
        tipo.value = c.tipo_dni
        nro.value = str(c.nro_dni)
        nombre.value = c.nombre
        apellido.value = c.apellido
        tipo.disabled = True        # el documento no se cambia al editar
        nro.disabled = True
        avisar(f"Editando: {c}")

    def cliente_elegido():
        """Devuelve el cliente que se está editando, o None si no hay ninguno."""
        if seleccionado["tipo"] is None:
            avisar("Primero elegí un cliente con 'Editar' en la tabla.", ok=False)
            return None
        return dao.buscar_por_documento(seleccionado["tipo"], seleccionado["nro"])

    # ---------- ACCIONES DE LOS BOTONES ----------
    def btn_alta(e):
        nuevo = Cliente((tipo.value or "").strip().upper(),
                        (nro.value or "").strip(),
                        (nombre.value or "").strip().title(),
                        (apellido.value or "").strip().title())
        error = nuevo.validar()
        if error:
            avisar("Error: " + error, ok=False)
            return
        existente = dao.buscar_por_documento(nuevo.tipo_dni, nuevo.nro_dni)
        if existente:
            if existente.estado == "Activo":
                avisar("Error: ya existe un cliente con ese documento.", ok=False)
                return
            # Estaba dado de baja: se lo da de alta de nuevo con los datos recién cargados
            dao.modificar(nuevo)
            limpiar()
            cargar_tabla()
            avisar(f"Cliente dado de alta nuevamente: {nuevo}")
            return
        dao.agregar(nuevo)
        limpiar()
        cargar_tabla()
        avisar(f"Cliente creado: {nuevo}")

    def btn_modificar(e):
        actual = cliente_elegido()
        if actual is None:
            return
        if actual.estado == "Inactivo":
            avisar("Error: no se puede modificar un cliente dado de baja.", ok=False)
            return
        modificado = Cliente(actual.tipo_dni, actual.nro_dni,
                             (nombre.value or "").strip().title(),
                             (apellido.value or "").strip().title(),
                             actual.estado)
        error = modificado.validar()
        if error:
            avisar("Error: " + error, ok=False)
            return
        dao.modificar(modificado)
        limpiar()
        cargar_tabla()
        avisar(f"Cliente actualizado: {modificado}")

    def btn_baja(e):
        cliente = cliente_elegido()
        if cliente is None:
            return
        if cliente.estado == "Inactivo":
            avisar("El cliente ya estaba dado de baja.", ok=False)
            return
        # TODO (cuando esté Mascota): no permitir la baja si tiene mascotas activas.
        cliente.estado = "Inactivo"     # no se borra, solo cambia el estado
        dao.modificar(cliente)
        limpiar()
        cargar_tabla()
        avisar(f"Baja realizada: {cliente}")

    def btn_limpiar(e):
        limpiar()
        avisar("Formulario limpio.")

    # ---------- ARMADO DE LA PANTALLA ----------
    cargar_tabla()
    page.add(ft.Column(controls=[
        ft.Text("ABM de Clientes", size=24, weight=ft.FontWeight.BOLD),
        ft.Row(controls=[tipo, nro, nombre, apellido], wrap=True),
        ft.Row(controls=[
            boton("Alta", btn_alta),
            boton("Modificar", btn_modificar),
            boton("Baja", btn_baja),
            boton("Limpiar", btn_limpiar, BOTON_BORDE),
        ], wrap=True),
        mensaje,
        mostrar_inactivos,
        ft.Column(controls=[tabla], scroll=ft.ScrollMode.AUTO),
    ]))


if __name__ == "__main__":
    if NUEVO_FLET:
        ft.run(pantallaCliente)
    else:
        ft.app(target=pantallaCliente)