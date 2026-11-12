from __future__ import annotations
import os
from pathlib import Path
import flet as ft
from src.infrastructure.reports.generador_pdf import GeneradorPDF
from src.ui.helpers import mostrar_mensaje


class ReportesView(ft.Container):
    """Vista minimalista para generar y abrir los 4 reportes obligatorios en PDF."""

    def __init__(self, page: ft.Page, generador_pdf: GeneradorPDF) -> None:
        super().__init__(padding=20, expand=True)
        self._page = page
        self._generador = generador_pdf
        self._lbl_ultimo_pdf = ft.Text(
            f"Carpeta de salida: {self._generador._output_dir}",
            selectable=True,
            color=ft.colors.BLUE_GREY_700,
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Text("Reportes Analíticos en PDF (ReportLab)", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Seleccione el reporte que desea generar. Se abrirá automáticamente tras crearse."),
                self._crear_tarjeta_reporte(
                    "1. Atenciones Clínicas y Derivaciones Realizadas",
                    "Detalle de consultas médicas, veterinario, diagnóstico y derivaciones emitidas.",
                    lambda e: self._generar_y_abrir(self._generador.generar_reporte_atenciones_y_derivaciones),
                ),
                self._crear_tarjeta_reporte(
                    "2. Muestras Biológicas Rechazadas en Transporte",
                    "Listado de muestras rechazadas por precinto roto o fallas durante la cadena de custodia.",
                    lambda e: self._generar_y_abrir(self._generador.generar_reporte_muestras_rechazadas),
                ),
                self._crear_tarjeta_reporte(
                    "3. Tratamientos Aplicados y Vacunas Pendientes",
                    "Resumen por mascota de tratamientos realizados y vacunas faltantes del esquema obligatorio.",
                    lambda e: self._generar_y_abrir(self._generador.generar_reporte_tratamientos_y_vacunas),
                ),
                self._crear_tarjeta_reporte(
                    "4. Tiempo Promedio de Tránsito y Procesamiento",
                    "Métricas operativas de horas en tránsito y procesamiento de muestras en laboratorio.",
                    lambda e: self._generar_y_abrir(self._generador.generar_reporte_tiempos_muestras),
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Generar los 4 Reportes PDF",
                            icon=ft.icons.DOWNLOAD_FOR_OFFLINE,
                            on_click=self._generar_todos,
                        ),
                        ft.OutlinedButton(
                            "Abrir Carpeta de Reportes",
                            icon=ft.icons.FOLDER_OPEN,
                            on_click=self._abrir_carpeta,
                        ),
                    ]
                ),
                self._lbl_ultimo_pdf,
            ],
        )

    def _crear_tarjeta_reporte(self, titulo: str, descripcion: str, handler) -> ft.Container:
        return ft.Container(
            padding=12,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=6,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=4,
                        expand=True,
                        controls=[
                            ft.Text(titulo, size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(descripcion, size=13, color=ft.colors.GREY_700),
                        ],
                    ),
                    ft.ElevatedButton("Generar PDF", icon=ft.icons.PICTURE_AS_PDF, on_click=handler),
                ],
            ),
        )

    def refrescar(self) -> None:
        pass

    def _generar_y_abrir(self, funcion_generadora) -> None:
        try:
            ruta: Path = funcion_generadora()
            self._lbl_ultimo_pdf.value = f"Último PDF generado: {ruta}"
            mostrar_mensaje(self._page, f"PDF generado correctamente: {ruta.name}")
            if os.name == "nt" and ruta.exists():
                try:
                    os.startfile(str(ruta))
                except Exception:
                    pass
            self._page.update()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error generando PDF: {ex}", es_error=True)

    def _generar_todos(self, e) -> None:
        try:
            r1 = self._generador.generar_reporte_atenciones_y_derivaciones()
            r2 = self._generador.generar_reporte_muestras_rechazadas()
            r3 = self._generador.generar_reporte_tratamientos_y_vacunas()
            r4 = self._generador.generar_reporte_tiempos_muestras()
            self._lbl_ultimo_pdf.value = (
                f"4 reportes generados en: {self._generador._output_dir} "
                f"({r1.name}, {r2.name}, {r3.name}, {r4.name})"
            )
            mostrar_mensaje(self._page, "Los 4 reportes PDF fueron generados correctamente.")
            self._page.update()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error generando los reportes: {ex}", es_error=True)

    def _abrir_carpeta(self, e) -> None:
        try:
            carpeta = self._generador._output_dir
            if os.name == "nt" and carpeta.exists():
                os.startfile(str(carpeta))
        except Exception as ex:
            mostrar_mensaje(self._page, f"No se pudo abrir la carpeta: {ex}", es_error=True)
