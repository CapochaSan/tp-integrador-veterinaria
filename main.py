from __future__ import annotations
import flet as ft

from src.infrastructure.database.db_manager import DBManager
from src.infrastructure.repositories.sqlite_repositorios import (
    SQLiteClienteRepositorio,
    SQLiteMascotaRepositorio,
    SQLiteTurnoRepositorio,
    SQLiteConsultaMedicaRepositorio,
    SQLiteComprobanteRepositorio,
    SQLiteOrdenDerivacionRepositorio,
    SQLiteRemitoBiologicoRepositorio,
    SQLiteMuestraBiologicaRepositorio,
)
from src.infrastructure.reports.generador_pdf import GeneradorPDF
from src.domain.services.cliente_service import ClinicaService
from src.domain.services.laboratorio_service import LaboratorioService
from src.ui.views.clientes_mascotas_view import ClientesMascotasView
from src.ui.views.turnos_view import TurnosView
from src.ui.views.consultas_view import ConsultasView
from src.ui.views.empaquetado_view import EmpaquetadoView
from src.ui.views.laboratorio_view import LaboratorioView
from src.ui.views.reportes_view import ReportesView


def construir_servicios():
    """Inicializa la base de datos (con seed si está vacía) e inyecta dependencias."""
    db_manager = DBManager()
    db_manager.inicializar_base_datos(cargar_seed=True)

    cliente_repo = SQLiteClienteRepositorio(db_manager)
    mascota_repo = SQLiteMascotaRepositorio(db_manager)
    turno_repo = SQLiteTurnoRepositorio(db_manager)
    consulta_repo = SQLiteConsultaMedicaRepositorio(db_manager)
    comprobante_repo = SQLiteComprobanteRepositorio(db_manager)
    orden_repo = SQLiteOrdenDerivacionRepositorio(db_manager)
    remito_repo = SQLiteRemitoBiologicoRepositorio(db_manager)
    muestra_repo = SQLiteMuestraBiologicaRepositorio(db_manager)

    clinica_service = ClinicaService(
        cliente_repo=cliente_repo,
        mascota_repo=mascota_repo,
        turno_repo=turno_repo,
        consulta_repo=consulta_repo,
        comprobante_repo=comprobante_repo,
    )
    lab_service = LaboratorioService(
        orden_repo=orden_repo,
        remito_repo=remito_repo,
        muestra_repo=muestra_repo,
        consulta_repo=consulta_repo,
        mascota_repo=mascota_repo,
    )
    generador_pdf = GeneradorPDF(db_manager)
    return clinica_service, lab_service, generador_pdf


def main(page: ft.Page) -> None:
    page.title = "Red de Clínicas Veterinarias & Laboratorio"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1150
    page.window.height = 780
    page.padding = 10

    clinica_service, lab_service, generador_pdf = construir_servicios()

    vista_clientes = ClientesMascotasView(page, clinica_service)
    vista_turnos = TurnosView(page, clinica_service)
    vista_consultas = ConsultasView(page, clinica_service, lab_service)
    vista_empaquetado = EmpaquetadoView(page, clinica_service, lab_service)
    vista_laboratorio = LaboratorioView(page, lab_service)
    vista_reportes = ReportesView(page, generador_pdf)

    vistas = [
        vista_clientes,
        vista_turnos,
        vista_consultas,
        vista_empaquetado,
        vista_laboratorio,
        vista_reportes,
    ]

    def on_tab_change(e: ft.ControlEvent) -> None:
        idx = e.control.selected_index
        if 0 <= idx < len(vistas):
            vistas[idx].refrescar()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=150,
        expand=True,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text="Clientes y Mascotas", icon=ft.icons.PETS, content=vista_clientes),
            ft.Tab(text="Turnos", icon=ft.icons.CALENDAR_MONTH, content=vista_turnos),
            ft.Tab(text="Consultas y Facturación", icon=ft.icons.MEDICAL_SERVICES, content=vista_consultas),
            ft.Tab(text="Empaquetado y Envíos", icon=ft.icons.INVENTORY_2, content=vista_empaquetado),
            ft.Tab(text="Laboratorio", icon=ft.icons.SCIENCE, content=vista_laboratorio),
            ft.Tab(text="Reportes PDF", icon=ft.icons.PICTURE_AS_PDF, content=vista_reportes),
        ],
    )

    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    bgcolor=ft.colors.BLUE_900,
                    border_radius=6,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Sistema Veterinaria & Derivación de Laboratorio",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                            ),
                            ft.Text("TP Integrador DAO 2026", color=ft.colors.BLUE_100, size=13),
                        ],
                    ),
                ),
                tabs,
            ],
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
