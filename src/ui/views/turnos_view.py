from __future__ import annotations
from datetime import datetime, timedelta
import flet as ft
from src.domain.services.cliente_service import ClinicaService
from src.ui.helpers import mostrar_mensaje


class TurnosView(ft.Container):
    """Vista minimalista para gestionar Turnos y evitar superposiciones."""

    def __init__(self, page: ft.Page, clinica_service: ClinicaService) -> None:
        super().__init__(padding=15, expand=True)
        self._page = page
        self._service = clinica_service

        manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        self._dd_mascota = ft.Dropdown(label="Mascota", width=260)
        self._dd_veterinario = ft.Dropdown(
            label="Veterinario",
            width=220,
            value="Dra. Ana López",
            options=[
                ft.dropdown.Option("Dra. Ana López"),
                ft.dropdown.Option("Dr. Carlos Ruiz"),
                ft.dropdown.Option("Dra. Sofía Torres"),
            ],
        )
        self._txt_fecha = ft.TextField(label="Fecha (YYYY-MM-DD)", value=manana, width=160)
        self._txt_hora = ft.TextField(label="Hora (HH:MM)", value="10:00", width=130)

        self._tabla_turnos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha y Hora")),
                ft.DataColumn(ft.Text("Mascota")),
                ft.DataColumn(ft.Text("Veterinario")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                ft.Text("Agenda de Turnos (Ventana de 30 min)", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    wrap=True,
                    controls=[
                        self._dd_mascota,
                        self._dd_veterinario,
                        self._txt_fecha,
                        self._txt_hora,
                        ft.ElevatedButton(
                            "Agendar Turno",
                            icon=ft.icons.EVENT_AVAILABLE,
                            on_click=self._on_agendar_turno,
                        ),
                    ],
                ),
                ft.Container(
                    content=ft.Row([self._tabla_turnos], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                ),
            ],
        )
        self.refrescar()

    def refrescar(self) -> None:
        mascotas = self._service.listar_mascotas()
        mapa_mascotas = {m.id: f"{m.nombre} ({m.especie})" for m in mascotas}

        self._dd_mascota.options = [
            ft.dropdown.Option(key=str(m.id), text=f"{m.id} - {m.nombre} ({m.especie})")
            for m in mascotas
        ]

        turnos = self._service.listar_turnos()
        filas = []
        for t in turnos:
            btn_cancelar = (
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e, id_t=t.id: self._on_cancelar_turno(id_t),
                )
                if t.estado == "Pendiente"
                else ft.Text("-")
            )
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(t.id))),
                        ft.DataCell(ft.Text(t.fecha_hora.strftime("%d/%m/%Y %H:%M"))),
                        ft.DataCell(ft.Text(mapa_mascotas.get(t.id_mascota, f"ID {t.id_mascota}"))),
                        ft.DataCell(ft.Text(t.veterinario)),
                        ft.DataCell(ft.Text(t.estado)),
                        ft.DataCell(btn_cancelar),
                    ]
                )
            )
        self._tabla_turnos.rows = filas
        if self._page:
            self._page.update()

    def _on_agendar_turno(self, e) -> None:
        try:
            if not self._dd_mascota.value:
                raise ValueError("Debe seleccionar una mascota.")
            fecha_str = f"{(self._txt_fecha.value or '').strip()} {(self._txt_hora.value or '').strip()}"
            fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
            self._service.agendar_turno(
                id_mascota=int(self._dd_mascota.value),
                veterinario=self._dd_veterinario.value or "Dra. Ana López",
                fecha_hora=fecha_hora,
            )
            mostrar_mensaje(self._page, "Turno agendado correctamente.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)

    def _on_cancelar_turno(self, id_turno: int) -> None:
        try:
            self._service.cancelar_turno(id_turno)
            mostrar_mensaje(self._page, f"Turno {id_turno} cancelado.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)
