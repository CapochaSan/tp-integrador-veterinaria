from __future__ import annotations
import flet as ft
from src.domain.services.cliente_service import ClinicaService
from src.ui.helpers import mostrar_mensaje


class ClientesMascotasView(ft.Container):
    """Vista minimalista para gestionar Clientes y Mascotas."""

    def __init__(self, page: ft.Page, clinica_service: ClinicaService) -> None:
        super().__init__(padding=15, expand=True)
        self._page = page
        self._service = clinica_service

        # Campos Cliente
        self._txt_nombre = ft.TextField(label="Nombre", width=180)
        self._txt_apellido = ft.TextField(label="Apellido", width=180)
        self._txt_dni = ft.TextField(label="DNI", width=140)
        self._txt_tel = ft.TextField(label="Teléfono", width=150)
        self._txt_email = ft.TextField(label="Email", width=200)

        self._tabla_clientes = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Apellido y Nombre")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Email")),
            ],
            rows=[],
        )

        # Campos Mascota
        self._dd_cliente = ft.Dropdown(label="Cliente / Tutor", width=260)
        self._txt_m_nombre = ft.TextField(label="Nombre Mascota", width=170)
        self._dd_especie = ft.Dropdown(
            label="Especie",
            width=140,
            value="Canino",
            options=[
                ft.dropdown.Option("Canino"),
                ft.dropdown.Option("Felino"),
                ft.dropdown.Option("Ave"),
                ft.dropdown.Option("Otro"),
            ],
        )
        self._txt_raza = ft.TextField(label="Raza", value="Mestizo", width=150)
        self._txt_edad = ft.TextField(label="Edad (años)", value="1", width=110)
        self._txt_peso = ft.TextField(label="Peso (kg)", value="5.0", width=110)

        self._tabla_mascotas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Mascota")),
                ft.DataColumn(ft.Text("Especie")),
                ft.DataColumn(ft.Text("Raza")),
                ft.DataColumn(ft.Text("Edad")),
                ft.DataColumn(ft.Text("Peso (kg)")),
                ft.DataColumn(ft.Text("Tutor")),
            ],
            rows=[],
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                ft.Text("Gestión de Clientes", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    wrap=True,
                    controls=[
                        self._txt_nombre,
                        self._txt_apellido,
                        self._txt_dni,
                        self._txt_tel,
                        self._txt_email,
                        ft.ElevatedButton(
                            "Registrar Cliente",
                            icon=ft.icons.PERSON_ADD,
                            on_click=self._on_guardar_cliente,
                        ),
                    ],
                ),
                ft.Container(
                    content=ft.Row([self._tabla_clientes], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                ),
                ft.Divider(),
                ft.Text("Gestión de Mascotas", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    wrap=True,
                    controls=[
                        self._dd_cliente,
                        self._txt_m_nombre,
                        self._dd_especie,
                        self._txt_raza,
                        self._txt_edad,
                        self._txt_peso,
                        ft.ElevatedButton(
                            "Registrar Mascota",
                            icon=ft.icons.PETS,
                            on_click=self._on_guardar_mascota,
                        ),
                    ],
                ),
                ft.Container(
                    content=ft.Row([self._tabla_mascotas], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                ),
            ],
        )
        self.refrescar()

    def refrescar(self) -> None:
        clientes = self._service.listar_clientes()
        mapa_clientes = {c.id: c.nombre_completo for c in clientes}

        self._tabla_clientes.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(c.id))),
                    ft.DataCell(ft.Text(c.nombre_completo)),
                    ft.DataCell(ft.Text(c.dni)),
                    ft.DataCell(ft.Text(c.telefono)),
                    ft.DataCell(ft.Text(c.email)),
                ]
            )
            for c in clientes
        ]

        self._dd_cliente.options = [
            ft.dropdown.Option(key=str(c.id), text=f"{c.nombre_completo} (DNI {c.dni})")
            for c in clientes
        ]

        mascotas = self._service.listar_mascotas()
        self._tabla_mascotas.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(m.id))),
                    ft.DataCell(ft.Text(m.nombre)),
                    ft.DataCell(ft.Text(m.especie)),
                    ft.DataCell(ft.Text(m.raza)),
                    ft.DataCell(ft.Text(str(m.edad))),
                    ft.DataCell(ft.Text(f"{m.peso:.1f}")),
                    ft.DataCell(ft.Text(mapa_clientes.get(m.id_cliente, f"ID {m.id_cliente}"))),
                ]
            )
            for m in mascotas
        ]
        if self._page:
            self._page.update()

    def _on_guardar_cliente(self, e) -> None:
        try:
            self._service.registrar_cliente(
                nombre=self._txt_nombre.value or "",
                apellido=self._txt_apellido.value or "",
                dni=self._txt_dni.value or "",
                telefono=self._txt_tel.value or "",
                email=self._txt_email.value or "",
            )
            self._txt_nombre.value = ""
            self._txt_apellido.value = ""
            self._txt_dni.value = ""
            self._txt_tel.value = ""
            self._txt_email.value = ""
            mostrar_mensaje(self._page, "Cliente registrado correctamente.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)

    def _on_guardar_mascota(self, e) -> None:
        try:
            if not self._dd_cliente.value:
                raise ValueError("Debe seleccionar un cliente válido.")
            id_cliente = int(self._dd_cliente.value)
            edad = int(self._txt_edad.value or 0)
            peso = float(self._txt_peso.value or 0.0)
            self._service.registrar_mascota(
                id_cliente=id_cliente,
                nombre=self._txt_m_nombre.value or "",
                especie=self._dd_especie.value or "Canino",
                raza=self._txt_raza.value or "Mestizo",
                edad=edad,
                peso=peso,
            )
            self._txt_m_nombre.value = ""
            self._txt_raza.value = "Mestizo"
            self._txt_edad.value = "1"
            self._txt_peso.value = "5.0"
            mostrar_mensaje(self._page, "Mascota registrada correctamente.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)
