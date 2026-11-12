from __future__ import annotations
import flet as ft
from src.domain.services.laboratorio_service import LaboratorioService
from src.ui.helpers import mostrar_mensaje


class LaboratorioView(ft.Container):
    """Vista para Recepción en Laboratorio (check precinto roto), Carga de Resultados y Trazabilidad."""

    def __init__(self, page: ft.Page, lab_service: LaboratorioService) -> None:
        super().__init__(padding=15, expand=True)
        self._page = page
        self._lab_service = lab_service

        # Sección Recepción
        self._dd_muestra_transito = ft.Dropdown(label="Muestra en Tránsito", width=330)
        self._chk_precinto_roto = ft.Checkbox(label="Precinto Roto / Violado (Rechazo automático)", value=False)
        self._txt_resp_rec = ft.TextField(label="Bioquímico / Responsable", value="Bioq. Sofía Méndez", width=220)

        # Sección Carga de Resultados
        self._dd_muestra_recibida = ft.Dropdown(label="Muestra para Análisis", width=330)
        self._txt_resultado = ft.TextField(
            label="Resultado del Análisis",
            hint_text="Ej: Valores dentro de parámetros normales",
            width=360,
        )

        # Tabla general de Muestras
        self._tabla_muestras = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Tipo Muestra")),
                ft.DataColumn(ft.Text("Precinto")),
                ft.DataColumn(ft.Text("Estado (State)")),
                ft.DataColumn(ft.Text("Resultado / Motivo Rechazo")),
                ft.DataColumn(ft.Text("Log")),
            ],
            rows=[],
        )

        # Visor de Log inmutable
        self._txt_log_trazabilidad = ft.TextField(
            label="Log Inmutable de Trazabilidad (con Timestamps)",
            multiline=True,
            min_lines=5,
            max_lines=10,
            read_only=True,
            expand=True,
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Text("1. Recepción en Laboratorio Central", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self._dd_muestra_transito,
                        self._chk_precinto_roto,
                        self._txt_resp_rec,
                        ft.ElevatedButton(
                            "Registrar Recepción",
                            icon=ft.icons.CHECK_CIRCLE_OUTLINE,
                            on_click=self._on_recibir_muestra,
                        ),
                    ],
                ),
                ft.Divider(),
                ft.Text("2. Carga de Resultados de Análisis", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    wrap=True,
                    controls=[
                        self._dd_muestra_recibida,
                        self._txt_resultado,
                        ft.ElevatedButton(
                            "Cargar Resultado",
                            icon=ft.icons.ASSIGNMENT_TURNED_IN,
                            on_click=self._on_cargar_resultado,
                        ),
                    ],
                ),
                ft.Divider(),
                ft.Text("3. Estado Actual y Trazabilidad de Muestras", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row([self._tabla_muestras], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                ),
                self._txt_log_trazabilidad,
            ],
        )
        self.refrescar()

    def refrescar(self) -> None:
        muestras = self._lab_service.listar_muestras()

        en_transito = [m for m in muestras if m.nombre_estado == "En Tránsito"]
        self._dd_muestra_transito.options = [
            ft.dropdown.Option(
                key=str(m.id),
                text=f"Muestra #{m.id} - {m.tipo_muestra} (Precinto: {m.codigo_precinto})",
            )
            for m in en_transito
        ]

        para_analisis = [m for m in muestras if m.nombre_estado in ("Recibida", "Rechazada")]
        self._dd_muestra_recibida.options = [
            ft.dropdown.Option(
                key=str(m.id),
                text=f"Muestra #{m.id} - {m.tipo_muestra} [{m.nombre_estado}]",
            )
            for m in para_analisis
        ]

        filas = []
        for m in muestras:
            color_estado = ft.colors.BLACK
            if m.nombre_estado == "Analizada":
                color_estado = ft.colors.GREEN_700
            elif m.nombre_estado == "Rechazada":
                color_estado = ft.colors.RED_700
            elif m.nombre_estado == "En Tránsito":
                color_estado = ft.colors.BLUE_700

            detalle = m.resultado or m.motivo_rechazo or "-"
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(m.id))),
                        ft.DataCell(ft.Text(m.tipo_muestra)),
                        ft.DataCell(ft.Text(f"{m.codigo_precinto} {'(ROTO)' if m.precinto_roto else ''}")),
                        ft.DataCell(ft.Text(m.nombre_estado, color=color_estado, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(detalle)),
                        ft.DataCell(
                            ft.TextButton(
                                "Ver Log",
                                on_click=lambda e, log=m.obtener_log_texto(): self._on_ver_log(log),
                            )
                        ),
                    ]
                )
            )
        self._tabla_muestras.rows = filas
        if self._page:
            self._page.update()

    def _on_ver_log(self, log: str) -> None:
        self._txt_log_trazabilidad.value = log
        self._page.update()

    def _on_recibir_muestra(self, e) -> None:
        try:
            if not self._dd_muestra_transito.value:
                raise ValueError("Seleccione una muestra en tránsito.")
            id_m = int(self._dd_muestra_transito.value)
            precinto_roto = bool(self._chk_precinto_roto.value)
            muestra = self._lab_service.recibir_muestra(
                id_muestra=id_m,
                precinto_roto=precinto_roto,
                responsable_recepcion=self._txt_resp_rec.value or "Laboratorio",
            )
            self._chk_precinto_roto.value = False
            self._txt_log_trazabilidad.value = muestra.obtener_log_texto()

            if muestra.nombre_estado == "Rechazada":
                mostrar_mensaje(
                    self._page,
                    f"Muestra #{muestra.id} RECHAZADA automáticamente por precinto roto.",
                    es_error=True,
                )
            else:
                mostrar_mensaje(self._page, f"Muestra #{muestra.id} recibida correctamente.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)

    def _on_cargar_resultado(self, e) -> None:
        try:
            if not self._dd_muestra_recibida.value:
                raise ValueError("Seleccione una muestra para analizar.")
            id_m = int(self._dd_muestra_recibida.value)
            muestra = self._lab_service.cargar_resultado_analisis(
                id_muestra=id_m,
                resultado=self._txt_resultado.value or "",
            )
            self._txt_resultado.value = ""
            self._txt_log_trazabilidad.value = muestra.obtener_log_texto()
            mostrar_mensaje(self._page, f"Muestra #{muestra.id} analizada y resultado registrado.")
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)
