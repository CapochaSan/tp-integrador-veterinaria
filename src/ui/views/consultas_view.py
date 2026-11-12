from __future__ import annotations
import flet as ft
from src.domain.services.cliente_service import ClinicaService
from src.domain.services.laboratorio_service import LaboratorioService
from src.ui.helpers import mostrar_mensaje


class ConsultasView(ft.Container):
    """Vista minimalista para Consultas Médicas, Control de Vacunas y Facturación (Strategy)."""

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

        self._dd_mascota = ft.Dropdown(
            label="Mascota",
            width=260,
            on_change=self._on_mascota_change,
        )
        self._lbl_vacunas_estado = ft.Text(
            "Seleccione una mascota para verificar su esquema de vacunas.",
            color=ft.colors.BLUE_GREY_700,
            weight=ft.FontWeight.W_500,
        )
        self._dd_veterinario = ft.Dropdown(
            label="Veterinario",
            width=200,
            value="Dra. Ana López",
            options=[
                ft.dropdown.Option("Dra. Ana López"),
                ft.dropdown.Option("Dr. Carlos Ruiz"),
                ft.dropdown.Option("Dra. Sofía Torres"),
            ],
        )
        self._txt_motivo = ft.TextField(label="Motivo", width=220)
        self._txt_diagnostico = ft.TextField(label="Diagnóstico", width=220)
        self._txt_tratamiento = ft.TextField(label="Tratamiento", width=240)
        self._txt_vacunas = ft.TextField(
            label="Vacunas aplicadas (separadas por coma)",
            hint_text="Ej: Rabia, Quíntuple",
            width=270,
        )

        # Facturación (Strategy)
        self._txt_monto = ft.TextField(label="Monto Base ($)", value="10000", width=140)
        self._dd_tarifa = ft.Dropdown(
            label="Tarifa (Strategy)",
            width=180,
            value="Normal",
            options=[
                ft.dropdown.Option("Normal", "Normal (Base)"),
                ft.dropdown.Option("Urgencia", "Urgencia (+50%)"),
            ],
        )

        # Derivación opcional a laboratorio
        self._chk_derivar = ft.Checkbox(
            label="Generar Orden de Derivación y Muestra a Laboratorio",
            value=False,
            on_change=self._on_toggle_derivar,
        )
        self._txt_estudio = ft.TextField(label="Tipo de Estudio", value="Hemograma Completo", width=200, visible=False)
        self._txt_tipo_muestra = ft.TextField(label="Tipo de Muestra", value="Sangre EDTA", width=180, visible=False)
        self._txt_precinto = ft.TextField(label="Código Precinto", value="PREC-2001", width=160, visible=False)

        self._tabla_consultas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Mascota")),
                ft.DataColumn(ft.Text("Diagnóstico")),
                ft.DataColumn(ft.Text("Tratamiento")),
                ft.DataColumn(ft.Text("Vacunas")),
                ft.DataColumn(ft.Text("Tarifa")),
                ft.DataColumn(ft.Text("Total ($)")),
            ],
            rows=[],
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                ft.Text("Registro de Consulta Médica y Comprobante", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(wrap=True, controls=[self._dd_mascota, self._dd_veterinario, self._txt_motivo]),
                self._lbl_vacunas_estado,
                ft.Row(wrap=True, controls=[self._txt_diagnostico, self._txt_tratamiento, self._txt_vacunas]),
                ft.Row(wrap=True, controls=[self._txt_monto, self._dd_tarifa]),
                self._chk_derivar,
                ft.Row(wrap=True, controls=[self._txt_estudio, self._txt_tipo_muestra, self._txt_precinto]),
                ft.ElevatedButton(
                    "Registrar Consulta y Emitir Comprobante",
                    icon=ft.icons.MEDICAL_SERVICES,
                    on_click=self._on_registrar_consulta,
                ),
                ft.Divider(),
                ft.Text("Historial de Consultas y Comprobantes", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row([self._tabla_consultas], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                ),
            ],
        )
        self.refrescar()

    def _on_toggle_derivar(self, e) -> None:
        visible = bool(self._chk_derivar.value)
        self._txt_estudio.visible = visible
        self._txt_tipo_muestra.visible = visible
        self._txt_precinto.visible = visible
        self._page.update()

    def _on_mascota_change(self, e) -> None:
        if not self._dd_mascota.value:
            return
        try:
            id_m = int(self._dd_mascota.value)
            al_dia, aplicadas, pendientes = self._clinica_service.obtener_esquema_vacunas_mascota(id_m)
            if al_dia:
                self._lbl_vacunas_estado.value = f"Esquema de vacunas AL DÍA (Aplicadas: {', '.join(aplicadas)})."
                self._lbl_vacunas_estado.color = ft.colors.GREEN_700
            else:
                self._lbl_vacunas_estado.value = (
                    f"VACUNAS PENDIENTES: {', '.join(pendientes)} | "
                    f"Aplicadas: {', '.join(aplicadas) if aplicadas else 'Ninguna'}"
                )
                self._lbl_vacunas_estado.color = ft.colors.ORANGE_800
            self._page.update()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error verificando vacunas: {ex}", es_error=True)

    def refrescar(self) -> None:
        mascotas = self._clinica_service.listar_mascotas()
        mapa_mascotas = {m.id: f"{m.nombre} ({m.especie})" for m in mascotas}

        self._dd_mascota.options = [
            ft.dropdown.Option(key=str(m.id), text=f"{m.id} - {m.nombre} ({m.especie})")
            for m in mascotas
        ]

        consultas = self._clinica_service.listar_consultas()
        comprobantes = self._clinica_service.listar_comprobantes()
        mapa_comp = {comp.id_consulta: comp for comp in comprobantes}

        filas = []
        for c in consultas:
            comp = mapa_comp.get(c.id)
            tarifa_txt = comp.tipo_tarifa if comp else "-"
            total_txt = f"${comp.total:,.2f}" if comp else "-"
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(c.id))),
                        ft.DataCell(ft.Text(c.fecha_hora.strftime("%d/%m/%Y %H:%M"))),
                        ft.DataCell(ft.Text(mapa_mascotas.get(c.id_mascota, f"ID {c.id_mascota}"))),
                        ft.DataCell(ft.Text(c.diagnostico or "-")),
                        ft.DataCell(ft.Text(c.tratamiento or "-")),
                        ft.DataCell(ft.Text(", ".join(c.vacunas_aplicadas) or "-")),
                        ft.DataCell(ft.Text(tarifa_txt)),
                        ft.DataCell(ft.Text(total_txt)),
                    ]
                )
            )
        self._tabla_consultas.rows = filas
        if self._page:
            self._page.update()

    def _on_registrar_consulta(self, e) -> None:
        try:
            if not self._dd_mascota.value:
                raise ValueError("Debe seleccionar una mascota.")
            id_mascota = int(self._dd_mascota.value)
            monto_base = float(self._txt_monto.value or 0.0)
            vacunas = [v.strip() for v in (self._txt_vacunas.value or "").split(",") if v.strip()]

            res = self._clinica_service.registrar_consulta_y_comprobante(
                id_mascota=id_mascota,
                motivo=self._txt_motivo.value or "",
                diagnostico=self._txt_diagnostico.value or "",
                tratamiento=self._txt_tratamiento.value or "",
                veterinario=self._dd_veterinario.value or "Dra. Ana López",
                vacunas_aplicadas=vacunas,
                monto_base=monto_base,
                tipo_tarifa=self._dd_tarifa.value or "Normal",
            )
            consulta = res["consulta"]
            comprobante = res["comprobante"]
            msg_vac = (
                "Vacunas al día."
                if res["vacunas_al_dia"]
                else f"Vacunas pendientes: {', '.join(res['vacunas_pendientes'])}"
            )

            if self._chk_derivar.value:
                self._lab_service.crear_orden_y_muestra(
                    id_consulta=consulta.id,
                    id_mascota=id_mascota,
                    tipo_estudio=self._txt_estudio.value or "Estudio General",
                    diagnostico_presuntivo=self._txt_diagnostico.value or "",
                    tipo_muestra=self._txt_tipo_muestra.value or "Sangre",
                    codigo_precinto=self._txt_precinto.value or f"PREC-{consulta.id}",
                )
                msg_vac += " | Orden y muestra extraída registradas."

            self._txt_motivo.value = ""
            self._txt_diagnostico.value = ""
            self._txt_tratamiento.value = ""
            self._txt_vacunas.value = ""
            mostrar_mensaje(
                self._page,
                f"Consulta #{consulta.id} registrada. Total ({comprobante.tipo_tarifa}): ${comprobante.total:,.2f}. {msg_vac}",
            )
            self._on_mascota_change(None)
            self.refrescar()
        except Exception as ex:
            mostrar_mensaje(self._page, f"Error: {ex}", es_error=True)
