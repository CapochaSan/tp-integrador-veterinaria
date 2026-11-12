from __future__ import annotations
from typing import Dict
import flet as ft
from src.domain.services.cliente_service import ClinicaService
from src.domain.services.laboratorio_service import LaboratorioService
from src.ui.helpers import mostrar_mensaje


class EmpaquetadoView(ft.Container):
    """Vista para Derivación, Empaquetado de Muestras en Conservadoras y Despacho de Remitos."""

    def __init__(
        self,
        page: ft.Page,
        clinica_service: ClinicaService,
        lab_service: LaboratorioService,
    ) -> None:
        super().__init__(padding=15, expand=True)
        self._page = page
        self._clinica_service = clinica_service
        self._lab_service = lab_service

        self._checkboxes_muestras: Dict[int, ft.Checkbox] = {}
        self._col_muestras_extraidas = ft.Column(spacing=5)

        # Nueva derivación rápida
        self._dd_consulta = ft.Dropdown(label="Consulta Médica", width=320)
        self._txt_estudio = ft.TextField(label="Tipo Estudio", value="Perfil Bioquímico", width=180)
        self._txt_muestra = ft.TextField(label="Tipo Muestra", value="Suero", width=150)
        self._txt_precinto = ft.TextField(label="Código Precinto", value="PREC-3001", width=150)

        # Datos del Remito
        self._txt_cod_remito = ft.TextField(label="Código Remito", value="REM-2026-003", width=170)
        self._txt_conservadora = ft.TextField(label="Conservadora", value="CONS-C3", width=150)
        self._txt_temp = ft.TextField(label="Temp (°C)", value="4.0", width=110)
        self._txt_resp = ft.TextField(label="Responsable Envío", value="Dra. Ana López", width=190)

        self._tabla_remitos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Código Remito")),
                ft.DataColumn(ft.Text("Conservadora")),
                ft.DataColumn(ft.Text("Temp (°C)")),
                ft.DataColumn(ft.Text("Responsable")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acción")),
            ],
            rows=[],
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
            controls=[
                ft.Text("1. Nueva Orden de Derivación / Extracción de Muestra", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    wrap=True,
                    controls=[
                        self._dd_consulta,
                        self._txt_estudio,
                        self._txt_muestra,
                        self._txt_precinto,
                        ft.ElevatedButton(
                            "Extraer Muestra",
                            icon=ft.icons.SCIENCE,
                            on_click=self._on_crear_derivacion,
                        ),
                    ],
                ),
                ft.Divider(),
                ft.Text("2. Empaquetado de Muestras Extraídas", size=18, weight=ft.FontWeight.BOLD),
                self._col_muestras_extraidas,
                ft.Row(
                    wrap=True,
                    controls=[
                        self._txt_cod_remito,
                        self._txt_conservadora,
                        self._txt_temp,
                        self._txt_resp,
                        ft.ElevatedButton(
                            "Empaquetar en Remito",
                            icon=ft.icons.INVENTORY_2,
                            on_click=self._on_empaquetar,
                        ),
                    ],
                ),
                ft.Divider(),
                ft.Text("3. Remitos Biológicos y Despacho", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row([self._tabla_remitos], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                ),
            ],
        )
        self.refrescar()

    def refrescar(self) -> None:
        consultas = self._clinica_service.listar_consultas()
        mascotas = {m.id: m.nombre for m in self._clinica_service.listar_mascotas()}
        self._dd_consulta.options = [
            ft.dropdown.Option(
                key=str(c.id),
                text=f"Consulta #{c.id} - {mascotas.get(c.id_mascota, '')} ({c.motivo})",
            )
            for c in consultas
        ]

        muestras = self._lab_service.listar_muestras()
        extraidas = [m for m in muestras if m.nombre_estado == "Extraída"]

        self._checkboxes_muestras.clear()
        controles_chk = []
        if not extraidas:
            controles_chk.append(ft.Text("No hay muestras pendientes de empaquetar.", italic=True))
        else:
            for m in extraidas:
                chk = ft.Checkbox(
                    label=f"Muestra #{m.id} | Orden #{m.id_orden} | {m.tipo_muestra} | Precinto: {m.codigo_precinto}",
                    value=False,
                )
                self._checkboxes_muestras[m.id] = chk
                controles_chk.append(chk)
        self._col_muestras_extraidas.controls = controles_chk

        remitos = self._lab_service.listar_remitos()
        filas = []
        for r in remitos:
            accion = (
                ft.ElevatedButton(
                    "Despachar a Tránsito",
                    icon=ft.icons.LOCAL_SHIPPING,
                    on_click=lambda e, id_r=r.id: self._on_despachar(id_r),
                )
                if r.estado == "Generado"
                else ft.Text(r.fecha_envio.strftime("%d/%m/%Y %H:%M") if r.fecha_envio else "-")
            )
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r.id))),
                        ft.DataCell(ft.Text(r.codigo_remito)),
                        ft.DataCell(ft.Text(r.codigo_conservadora)),
                        ft.DataCell(ft.Text(f"{r.temperatura_transporte:.1f} °C")),
                        ft.DataCell(ft.Text(r.responsable_envio)),
                        ft.DataCell(ft.Text(r.estado)),
                        ft.DataCell(accion),
                    ]
                )
            )
        self._tabla_remitos.rows = filas
        if self._page:
            self._page.update()

    def _on_crear_derivacion(self, e) -> None:
        try:
            if not self._dd_consulta.value:
                raise ValueError("Seleccione una consulta médica.")
            id_consulta = int(self._dd_consulta.value)
            consulta = next((c for c in self._clinica_service.listar_consultas() if c.id == id_consulta), None)
            if consulta is None:
                raise ValueError("Consulta no encontrada.")

            orden, muestra = self._lab_service.crear_orden_y_muestra(
                id_consulta=consulta.id,
                id_mascota=consulta.id_mascota,
                tipo_estudio=self._txt_estudio.value or "Estudio General",
                diagnostico_presuntivo=consulta.diagnostico,
                tipo_muestra=self._txt_muestra.value or "Sangre",
                codigo_precinto=self._txt_precinto.value or f"PREC-{consulta.id}",
            )
            mostrar_mensaje(self._page, f"Orden #{orden.id} y Muestra #{muestra.id} (Extraída) registradas.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)

    def _on_empaquetar(self, e) -> None:
        try:
            ids = [id_m for id_m, chk in self._checkboxes_muestras.items() if chk.value]
            temp = float(self._txt_temp.value or 4.0)
            remito = self._lab_service.empaquetar_muestras(
                ids_muestras=ids,
                codigo_remito=self._txt_cod_remito.value or "",
                codigo_conservadora=self._txt_conservadora.value or "",
                temperatura_transporte=temp,
                responsable_envio=self._txt_resp.value or "Clínica",
            )
            mostrar_mensaje(self._page, f"Remito {remito.codigo_remito} generado con {len(ids)} muestra(s) empaquetada(s).")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)

    def _on_despachar(self, id_remito: int) -> None:
        try:
            remito = self._lab_service.despachar_remito(id_remito)
            mostrar_mensaje(self._page, f"Remito {remito.codigo_remito} despachado a tránsito.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)
