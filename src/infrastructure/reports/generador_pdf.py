from __future__ import annotations
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

# Compatibilidad para ReportLab 4.4+ en Python 3.8 (usedforsecurity se introdujo en Python 3.9)
if sys.version_info < (3, 9):
    _orig_md5 = hashlib.md5

    def _md5_py38_compat(*args, **kwargs):
        kwargs.pop("usedforsecurity", None)
        return _orig_md5(*args, **kwargs)

    hashlib.md5 = _md5_py38_compat

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from config import REPORTES_DIR, VACUNAS_OBLIGATORIAS
from src.infrastructure.database.db_manager import DBManager


class GeneradorPDF:
    """Generador de los 4 reportes obligatorios en PDF utilizando ReportLab."""

    def __init__(self, db_manager: DBManager, output_dir: Path = REPORTES_DIR) -> None:
        self._db = db_manager
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._styles = getSampleStyleSheet()
        self._cell_style = ParagraphStyle(
            "CellStyle",
            parent=self._styles["Normal"],
            fontSize=8.5,
            leading=10.5,
        )
        self._header_cell_style = ParagraphStyle(
            "HeaderCellStyle",
            parent=self._styles["Normal"],
            fontSize=9,
            leading=11,
            textColor=colors.white,
        )

    def _p(self, texto: str, es_header: bool = False) -> Paragraph:
        estilo = self._header_cell_style if es_header else self._cell_style
        safe = str(texto or "-").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if es_header:
            safe = f"<b>{safe}</b>"
        return Paragraph(safe, estilo)

    def _crear_documento(
        self, nombre_archivo: str, titulo: str, subtitulo: str, horizontal: bool = True
    ) -> Tuple[Path, SimpleDocTemplate, List]:
        ruta = self._output_dir / nombre_archivo
        pagesize = landscape(A4) if horizontal else A4
        doc = SimpleDocTemplate(
            str(ruta),
            pagesize=pagesize,
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30,
        )
        elementos: List = []
        elementos.append(Paragraph(titulo, self._styles["Title"]))
        fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M")
        elementos.append(Paragraph(f"{subtitulo} — Generado el {fecha_gen}", self._styles["Normal"]))
        elementos.append(Spacer(1, 14))
        return ruta, doc, elementos

    def _estilo_tabla_simple(self) -> TableStyle:
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])

    def generar_reporte_atenciones_y_derivaciones(
        self, nombre_archivo: str = "reporte_1_atenciones_derivaciones.pdf"
    ) -> Path:
        """Reporte 1: Atenciones clínicas y derivaciones realizadas."""
        ruta, doc, elementos = self._crear_documento(
            nombre_archivo,
            "Reporte 1: Atenciones Clínicas y Derivaciones Realizadas",
            "Red de Clínicas Veterinarias",
        )

        with self._db.get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id, c.fecha_hora, m.nombre AS mascota, m.especie,
                       cl.apellido || ', ' || cl.nombre AS cliente,
                       c.veterinario, c.diagnostico,
                       od.tipo_estudio, od.diagnostico_presuntivo
                FROM consultas_medicas c
                JOIN mascotas m ON c.id_mascota = m.id
                JOIN clientes cl ON m.id_cliente = cl.id
                LEFT JOIN ordenes_derivacion od ON od.id_consulta = c.id
                ORDER BY c.fecha_hora DESC;
            """).fetchall()

        encabezados = [
            self._p("Fecha / Hora", True),
            self._p("Mascota", True),
            self._p("Tutor", True),
            self._p("Veterinario", True),
            self._p("Diagnóstico Clínico", True),
            self._p("Derivación a Lab", True),
        ]
        datos = [encabezados]

        for r in rows:
            derivacion = (
                f"Sí: {r['tipo_estudio']} ({r['diagnostico_presuntivo'] or '-'})"
                if r["tipo_estudio"]
                else "No requerida"
            )
            datos.append([
                self._p(r["fecha_hora"]),
                self._p(f"{r['mascota']} ({r['especie']})"),
                self._p(r["cliente"]),
                self._p(r["veterinario"]),
                self._p(r["diagnostico"] or "-"),
                self._p(derivacion),
            ])

        if len(datos) == 1:
            datos.append([self._p("Sin registros"), self._p("-"), self._p("-"), self._p("-"), self._p("-"), self._p("-")])

        tabla = Table(datos, colWidths=[110, 105, 115, 110, 150, 190], repeatRows=1)
        tabla.setStyle(self._estilo_tabla_simple())
        elementos.append(tabla)
        doc.build(elementos)
        return ruta

    def generar_reporte_muestras_rechazadas(
        self, nombre_archivo: str = "reporte_2_muestras_rechazadas.pdf"
    ) -> Path:
        """Reporte 2: Muestras biológicas rechazadas por fallas en el transporte."""
        ruta, doc, elementos = self._crear_documento(
            nombre_archivo,
            "Reporte 2: Muestras Biológicas Rechazadas",
            "Control de Calidad y Cadena de Custodia en Transporte",
        )

        with self._db.get_connection() as conn:
            rows = conn.execute("""
                SELECT mb.id, mb.tipo_muestra, mb.codigo_precinto, mb.precinto_roto,
                       mb.fecha_recepcion, mb.motivo_rechazo,
                       rb.codigo_remito, rb.codigo_conservadora, rb.temperatura_transporte,
                       m.nombre AS mascota
                FROM muestras_biologicas mb
                JOIN ordenes_derivacion od ON mb.id_orden = od.id
                JOIN mascotas m ON od.id_mascota = m.id
                LEFT JOIN remitos_biologicos rb ON mb.id_remito = rb.id
                WHERE LOWER(mb.estado) = 'rechazada'
                ORDER BY mb.id DESC;
            """).fetchall()

        encabezados = [
            self._p("ID", True),
            self._p("Mascota", True),
            self._p("Tipo Muestra", True),
            self._p("Precinto", True),
            self._p("Remito / Conservadora", True),
            self._p("Fecha Recepción", True),
            self._p("Motivo de Rechazo", True),
        ]
        datos = [encabezados]

        for r in rows:
            remito_txt = (
                f"{r['codigo_remito']} ({r['codigo_conservadora']}, {r['temperatura_transporte']}°C)"
                if r["codigo_remito"]
                else "Sin remito"
            )
            precinto_txt = f"{r['codigo_precinto']} ({'ROTO' if r['precinto_roto'] else 'Intacto'})"
            datos.append([
                self._p(str(r["id"])),
                self._p(r["mascota"]),
                self._p(r["tipo_muestra"]),
                self._p(precinto_txt),
                self._p(remito_txt),
                self._p(r["fecha_recepcion"] or "-"),
                self._p(r["motivo_rechazo"] or "Falla en transporte"),
            ])

        if len(datos) == 1:
            datos.append([self._p("-"), self._p("No se registran muestras rechazadas"), self._p("-"), self._p("-"), self._p("-"), self._p("-"), self._p("-")])

        tabla = Table(datos, colWidths=[35, 85, 100, 100, 155, 105, 200], repeatRows=1)
        tabla.setStyle(self._estilo_tabla_simple())
        elementos.append(tabla)
        doc.build(elementos)
        return ruta

    def generar_reporte_tratamientos_y_vacunas(
        self, nombre_archivo: str = "reporte_3_tratamientos_vacunas.pdf"
    ) -> Path:
        """Reporte 3: Tratamientos aplicados y vacunas pendientes por mascota."""
        ruta, doc, elementos = self._crear_documento(
            nombre_archivo,
            "Reporte 3: Tratamientos Aplicados y Vacunas Pendientes por Mascota",
            "Seguimiento Preventivo y Terapéutico",
        )

        with self._db.get_connection() as conn:
            mascotas = conn.execute("""
                SELECT m.id, m.nombre, m.especie, cl.apellido || ', ' || cl.nombre AS tutor
                FROM mascotas m
                JOIN clientes cl ON m.id_cliente = cl.id
                ORDER BY m.nombre;
            """).fetchall()

            consultas = conn.execute("""
                SELECT id_mascota, tratamiento, vacunas_aplicadas, fecha_hora
                FROM consultas_medicas
                ORDER BY fecha_hora ASC;
            """).fetchall()

        encabezados = [
            self._p("Mascota (Especie)", True),
            self._p("Tutor", True),
            self._p("Tratamientos Aplicados", True),
            self._p("Vacunas Aplicadas", True),
            self._p("Vacunas Pendientes", True),
            self._p("Estado", True),
        ]
        datos = [encabezados]

        for m in mascotas:
            trats = []
            aplicadas = []
            aplicadas_lower = set()
            for c in consultas:
                if c["id_mascota"] == m["id"]:
                    if c["tratamiento"] and c["tratamiento"].strip():
                        trats.append(f"- {c['tratamiento'].strip()}")
                    for v in (c["vacunas_aplicadas"] or "").split(","):
                        v_limpia = v.strip()
                        if v_limpia and v_limpia.lower() not in aplicadas_lower:
                            aplicadas_lower.add(v_limpia.lower())
                            aplicadas.append(v_limpia)

            obligatorias = VACUNAS_OBLIGATORIAS.get(m["especie"], VACUNAS_OBLIGATORIAS["General"])
            pendientes = [v for v in obligatorias if v.lower() not in aplicadas_lower]
            estado_vac = "Al día" if not pendientes else "Pendiente"

            datos.append([
                self._p(f"{m['nombre']} ({m['especie']})"),
                self._p(m["tutor"]),
                self._p("\n".join(trats) if trats else "Sin tratamientos registrados"),
                self._p(", ".join(aplicadas) if aplicadas else "Ninguna"),
                self._p(", ".join(pendientes) if pendientes else "Ninguna"),
                self._p(estado_vac),
            ])

        if len(datos) == 1:
            datos.append([self._p("Sin mascotas"), self._p("-"), self._p("-"), self._p("-"), self._p("-"), self._p("-")])

        tabla = Table(datos, colWidths=[115, 115, 200, 130, 145, 75], repeatRows=1)
        tabla.setStyle(self._estilo_tabla_simple())
        elementos.append(tabla)
        doc.build(elementos)
        return ruta

    def generar_reporte_tiempos_muestras(
        self, nombre_archivo: str = "reporte_4_tiempos_muestras.pdf"
    ) -> Path:
        """Reporte 4: Tiempo promedio de tránsito y procesamiento de muestras."""
        ruta, doc, elementos = self._crear_documento(
            nombre_archivo,
            "Reporte 4: Tiempo Promedio de Tránsito y Procesamiento de Muestras",
            "Indicadores de Eficiencia Operativa del Laboratorio",
        )

        with self._db.get_connection() as conn:
            rows = conn.execute("""
                SELECT id, tipo_muestra, estado, fecha_extraccion, fecha_recepcion, fecha_analisis
                FROM muestras_biologicas
                ORDER BY id ASC;
            """).fetchall()

        encabezados = [
            self._p("ID", True),
            self._p("Tipo Muestra", True),
            self._p("Estado", True),
            self._p("Extracción", True),
            self._p("Recepción", True),
            self._p("Análisis", True),
            self._p("Tránsito (hs)", True),
            self._p("Proceso Lab (hs)", True),
        ]
        datos = [encabezados]

        tiempos_transito: List[float] = []
        tiempos_proceso: List[float] = []

        for r in rows:
            dt_ext = _parse_dt(r["fecha_extraccion"])
            dt_rec = _parse_dt(r["fecha_recepcion"])
            dt_ana = _parse_dt(r["fecha_analisis"])

            transito_str = "-"
            proceso_str = "-"

            if dt_ext and dt_rec:
                horas_transito = round((dt_rec - dt_ext).total_seconds() / 3600.0, 2)
                tiempos_transito.append(horas_transito)
                transito_str = f"{horas_transito:.2f} h"

            if dt_rec and dt_ana:
                horas_proceso = round((dt_ana - dt_rec).total_seconds() / 3600.0, 2)
                tiempos_proceso.append(horas_proceso)
                proceso_str = f"{horas_proceso:.2f} h"

            datos.append([
                self._p(str(r["id"])),
                self._p(r["tipo_muestra"]),
                self._p(r["estado"]),
                self._p(r["fecha_extraccion"] or "-"),
                self._p(r["fecha_recepcion"] or "-"),
                self._p(r["fecha_analisis"] or "-"),
                self._p(transito_str),
                self._p(proceso_str),
            ])

        prom_transito = sum(tiempos_transito) / len(tiempos_transito) if tiempos_transito else 0.0
        prom_proceso = sum(tiempos_proceso) / len(tiempos_proceso) if tiempos_proceso else 0.0

        tabla = Table(datos, colWidths=[30, 100, 75, 110, 110, 110, 115, 130], repeatRows=1)
        tabla.setStyle(self._estilo_tabla_simple())
        elementos.append(tabla)
        elementos.append(Spacer(1, 16))
        elementos.append(
            Paragraph(
                f"<b>Resumen de Promedios:</b> "
                f"Tiempo promedio de tránsito: <b>{prom_transito:.2f} horas</b> "
                f"(sobre {len(tiempos_transito)} muestras recibidas) | "
                f"Tiempo promedio de procesamiento en laboratorio: <b>{prom_proceso:.2f} horas</b> "
                f"(sobre {len(tiempos_proceso)} muestras analizadas).",
                self._styles["Normal"],
            )
        )
        doc.build(elementos)
        return ruta


def _parse_dt(valor: Optional[str]) -> Optional[datetime]:
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None
