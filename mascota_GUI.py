from abc import ABC, abstractmethod

from mascota import Mascota
from mascota_dao import MascotaDAO
import flet as ft
from cliente_dao import ClienteDAO

cliente_dao = ClienteDAO()

dao = MascotaDAO()


def estado_mascota(mascota):
    """Obtiene el estado si existe; si el modelo usa activo, lo convierte."""
    estado = getattr(mascota, "estado", None)
    if estado is not None:
        return estado
    activo = getattr(mascota, "activo", None)
    if activo is not None:
        return "Activo" if activo else "Inactivo"
    return "Activo"


class avisar(ABC):
    """Interfaz para mostrar mensajes de éxito o error."""

    @abstractmethod
    def mostrar(self, texto, ok=True):
        """Muestra un mensaje."""
        raise NotImplementedError

    @abstractmethod
    def error(self, texto):
        """Muestra un mensaje de error."""
        raise NotImplementedError

    @abstractmethod
    def ok(self, texto):
        """Muestra un mensaje de éxito."""
        raise NotImplementedError


class AvisoConsola(avisar):
    """Implementación útil de avisar para consola."""

    def mostrar(self, texto, ok=True):
        prefijo = "OK" if ok else "ERROR"
        mensaje = f"[{prefijo}] {texto}"
        print(mensaje)
        return {"texto": texto, "ok": ok, "mensaje": mensaje}

    def error(self, texto):
        return self.mostrar(texto, ok=False)

    def ok(self, texto):
        return self.mostrar(texto, ok=True)


def mostrar_mensaje(*args, **kwargs):
    """Muestra un mensaje útil por consola y devuelve el resultado."""
    texto = args[0] if args else kwargs.get("texto") or kwargs.get("message") or ""
    ok = kwargs.get("ok", True)
    return AvisoConsola().mostrar(texto, ok=ok)


def alta():
    nombre = input("Nombre: ").strip().title()
    especie = input("Especie: ").strip().title()
    cliente = input("Cliente: ").strip().title()

    tipo_dni = "DNI"
    nro_dni = (cliente.value or "").strip()

    cliente_obj = cliente_dao.buscar_por_documento(tipo_dni, nro_dni)

    if cliente_obj is None:
        mostrar_mensaje("No existe un cliente con ese DNI")
        return

    nuevo = Mascota(
        (nombre.value or "").strip().title(),
        (especie.value or "").strip().title(),
        cliente_obj
)

    error = nuevo.validar()
    if error:
        print("Error:", error)
        return

    existente = dao.buscar_por_nombre(
            nuevo.nombre,
            nuevo.cliente.tipo_dni,
            nuevo.cliente.nro_dni
        )
    if existente:
        if estado_mascota(existente) == "Activo":
            print("Error: ya existe una mascota con ese nombre.")
            return
        # La mascota inactiva se reactiva con los datos ingresados.
        dao.modificar(nuevo)
        print("Mascota dada de alta nuevamente:", nuevo)
        return

    dao.agregar(nuevo)
    print("Mascota creada:", nuevo)


def listar():
    incluir = input("¿Incluir inactivos? (s/n): ").strip().lower() == "s"
    mascotas = dao.listar(incluir)
    if len(mascotas) == 0:
        print("No hay mascotas.")
    for mascota in mascotas:
        print(mascota)


def buscar():
    nombre = input("Nombre de la mascota: ").strip().title()
    mascota = dao.buscar_por_nombre(
            nuevo.nombre,
            nuevo.cliente.tipo_dni,
            nuevo.cliente.nro_dni
        )
    if mascota is None:
        print("No existe una mascota con ese nombre.")
    else:
        print(mascota)


def pedir_nombre_mascota():
    texto = input("Nombre de la mascota: ").strip().title()
    if not texto:
        print("Error: el nombre de la mascota es obligatorio.")
        return None
    return texto


def modificar():
    nombre = pedir_nombre_mascota()
    if nombre is None:
        return
    mascota = dao.buscar_por_nombre(
            nuevo.nombre,
            nuevo.cliente.tipo_dni,
            nuevo.cliente.nro_dni
        )
    if mascota is None:
        print("No existe una mascota con ese nombre.")
        return

    print("Actual:", mascota, "(Enter para dejar el valor como está)")
    nombre = input(f"Nombre [{mascota.nombre}]: ").strip().title() or mascota.nombre
    especie = input(f"Especie [{mascota.especie}]: ").strip().title() or mascota.especie

    modificado = Mascota(nombre, especie, mascota.cliente)
    modificado.estado = estado_mascota(mascota)

    error = modificado.validar()
    if error:
        print("Error:", error)
        return

    dao.modificar(modificado)
    print("Mascota actualizada:", modificado)


def baja():
    nombre = pedir_nombre_mascota()
    if nombre is None:
        return
    mascota = dao.buscar_por_nombre(
            nuevo.nombre,
            nuevo.cliente.tipo_dni,
            nuevo.cliente.nro_dni
        )
    if mascota is None:
        print("No existe una mascota con ese nombre.")
        return
    if estado_mascota(mascota) == "Inactivo":
        print("La mascota ya estaba dada de baja.")
        return

    mascota.estado = "Inactivo"     # do not delete, only change the state
    dao.modificar(
        mascota,
        nombre_original=mascota.nombre
    )
    print("Baja realizada:", mascota)



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
    """Crea un botón con texto compatible con distintas versiones de Flet."""
    clase = clase or BOTON
    if NUEVO_FLET:
        try:
            return clase(text=texto, on_click=accion)
        except TypeError:
            return clase(content=ft.Text(texto), on_click=accion)
    return clase(text=texto, on_click=accion)


def pantallaMascota(page: ft.Page):
    page.title = "Gestión de Mascotas"
    page.scroll = ft.ScrollMode.AUTO

    # Nombre de la mascota seleccionada para modificar o dar de baja.
    seleccionado = {"nombre": None, "tipo_dni": None, "nro_dni": None}

    # ---------- CAMPOS Y TABLA ----------
    nombre = ft.TextField(label="Nombre", width=200)
    especie = ft.TextField(label="Especie", width=200)
    tipo_dni = ft.Dropdown(
    label="Tipo de documento",
    width=160,
    options=[
        ft.dropdown.Option("DNI"),
        ft.dropdown.Option("CUIT"),
        ft.dropdown.Option("Pasaporte")
    ],
    value="DNI"
    )

    cliente = ft.TextField(
        label="Número de documento",
        width=200
)
    mostrar_inactivos = ft.Checkbox(label="Mostrar inactivos", value=False,
                                    on_change=lambda e: refrescar())
    mensaje = ft.Text("")           # acá aparecen los avisos y errores
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nombre")),
            ft.DataColumn(label=ft.Text("Especie")),
            ft.DataColumn(label=ft.Text("Cliente asociado")),
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
        seleccionado["nombre"] = None
        seleccionado["tipo_dni"] = None
        seleccionado["nro_dni"] = None
        nombre.value = ""
        especie.value = ""
        tipo_dni.value = ""
        cliente.value = ""

    def cargar_tabla():
        """Vuelve a llenar la tabla con las mascotas."""
        tabla.rows = []
        for mascota in dao.listar(mostrar_inactivos.value) or []:
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(content=ft.Text(mascota.nombre)),
                ft.DataCell(content=ft.Text(mascota.especie)),
                ft.DataCell(content=ft.Text(str(mascota.cliente))),
                ft.DataCell(content=ft.Text(estado_mascota(mascota))),
                ft.DataCell(content=boton(
                    "Editar",
                    lambda _event, mascota_obj=mascota: seleccionar(mascota_obj),
                    BOTON_TEXTO)),
            ]))

    def refrescar():
        cargar_tabla()
        page.update()

    def seleccionar(mascota_obj):
        """Al apretar 'Editar' en una fila, pasa los datos al formulario."""
        mascota = mascota_obj if isinstance(mascota_obj, Mascota) else dao.buscar_por_nombre(
            mascota_obj,
            tipo_dni.value,
            int((cliente.value or "0").strip() or 0),
        )
        if mascota is None:
            avisar("No existe esa mascota.", ok=False)
            return
        seleccionado["nombre"] = mascota.nombre
        seleccionado["tipo_dni"] = mascota.cliente.tipo_dni
        seleccionado["nro_dni"] = mascota.cliente.nro_dni
        nombre.value = mascota.nombre
        especie.value = mascota.especie
        tipo_dni.value = mascota.cliente.tipo_dni
        cliente.value = str(mascota.cliente.nro_dni)
        avisar(f"Editando mascota: {mascota}")

    def mascota_elegida():
        """Devuelve la mascota seleccionada, o None si no hay ninguna."""
        if seleccionado["nombre"] is None:
            avisar("Primero elegí una mascota con 'Editar' en la tabla.", ok=False)
            return None
        return dao.buscar_por_nombre(
            seleccionado["nombre"],
            seleccionado["tipo_dni"],
            seleccionado["nro_dni"],
        )

    # ---------- ACCIONES DE LOS BOTONES ----------
    def btn_alta(e):
        tipo = tipo_dni.value
        nro = (cliente.value or "").strip()

        if not tipo or not nro:
            avisar("Seleccioná el tipo e ingresá el número de documento.", ok=False)
            return

        cliente_obj = cliente_dao.buscar_por_documento(tipo, nro)

        if cliente_obj is None:
            avisar("No existe un cliente con ese documento.", ok=False)
            return

        nuevo = Mascota(
            (nombre.value or "").strip().title(),
            (especie.value or "").strip().title(),
            cliente_obj
        )

        error = nuevo.validar()
        if error:
            avisar("Error: " + error, ok=False)
            return

        existente = dao.buscar_por_nombre(
            nuevo.nombre,
            nuevo.cliente.tipo_dni,
            nuevo.cliente.nro_dni
        )

        if existente:
            if estado_mascota(existente) == "Activo":
                avisar("Error: ya existe una mascota con ese nombre.", ok=False)
                return

            dao.modificar(nuevo)
            limpiar()
            cargar_tabla()
            avisar(f"Mascota dada de alta nuevamente: {nuevo}")
            return

        dao.agregar(nuevo)
        limpiar()
        cargar_tabla()
        avisar(f"Mascota creada: {nuevo}")

    def btn_modificar(e):
        actual = mascota_elegida()

        if actual is None:
            return

        if estado_mascota(actual) == "Inactivo":
            avisar("No se puede modificar una mascota dada de baja.", ok=False)
            return

        modificado = Mascota(
            (nombre.value or "").strip().title(),
            (especie.value or "").strip().title(),
            actual.cliente
        )

        error = modificado.validar()
        if error:
            avisar("Error: " + error, ok=False)
            return

        actualizado = dao.modificar(
            modificado,
            nombre_original=actual.nombre
        )

        if actualizado:
            limpiar()
            cargar_tabla()
            avisar(f"Mascota actualizada: {modificado}")
        else:
            avisar("No se encontró la mascota para modificar.", ok=False)
            
    def btn_baja(e):
        mascota_seleccionada = mascota_elegida()
        if mascota_seleccionada is None:
            return
        if estado_mascota(mascota_seleccionada) == "Inactivo":
            avisar("La mascota ya estaba dada de baja.", ok=False)
            return
        mascota_seleccionada.estado = "Inactivo"     # no se borra, solo cambia el estado
        dao.modificar(mascota_seleccionada, nombre_original=mascota_seleccionada.nombre)
        limpiar()
        cargar_tabla()
        avisar(f"Baja realizada: {mascota_seleccionada}")

    def btn_limpiar(e):
        limpiar()
        avisar("Formulario limpio.")

    # ---------- ARMADO DE LA PANTALLA ----------
    cargar_tabla()
    page.add(ft.Column(controls=[
        ft.Text("ABM de Mascotas", size=24, weight=ft.FontWeight.BOLD),
    ft.Row(
    controls=[nombre, especie, tipo_dni, cliente],
    wrap=True
),        ft.Row(controls=[
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
        ft.run(pantallaMascota)
    else:
        ft.app(target=pantallaMascota)