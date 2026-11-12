from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from src.infrastructure.database.db_manager import DBManager
from src.domain.interfaces.repositorios import (
    IClienteRepositorio,
    IMascotaRepositorio,
    ITurnoRepositorio,
    IConsultaMedicaRepositorio,
    IComprobanteRepositorio,
    IOrdenDerivacionRepositorio,
    IRemitoBiologicoRepositorio,
    IMuestraBiologicaRepositorio,
)
from src.domain.models.cliente import Cliente
from src.domain.models.mascota import Mascota
from src.domain.models.turno import Turno
from src.domain.models.consulta_medica import ConsultaMedica
from src.domain.models.comprobante import ComprobanteAtencion
from src.domain.models.orden_derivacion import OrdenDerivacion
from src.domain.models.remito_biologico import RemitoBiologico
from src.domain.models.muestra_biologica import MuestraBiologica
from src.domain.patterns.estado_muestra import EstadoMuestra
from src.domain.patterns.estrategia_facturacion import obtener_estrategia


FMT_FECHA = "%Y-%m-%d %H:%M:%S"


def _str_a_dt(valor: Optional[str]) -> Optional[datetime]:
    if not valor:
        return None
    try:
        return datetime.strptime(valor, FMT_FECHA)
    except ValueError:
        return datetime.fromisoformat(valor)


def _dt_a_str(valor: Optional[datetime]) -> Optional[str]:
    if valor is None:
        return None
    return valor.strftime(FMT_FECHA)


class SQLiteClienteRepositorio(IClienteRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> Cliente:
        return Cliente(
            id_cliente=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            dni=row["dni"],
            telefono=row["telefono"] or "",
            email=row["email"] or "",
        )

    def guardar(self, cliente: Cliente) -> Cliente:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nombre, apellido, dni, telefono, email) VALUES (?, ?, ?, ?, ?);",
                (cliente.nombre, cliente.apellido, cliente.dni, cliente.telefono, cliente.email),
            )
            conn.commit()
            cliente.id = cursor.lastrowid
        return cliente

    def obtener_por_id(self, id_cliente: int) -> Optional[Cliente]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM clientes WHERE id = ?;", (id_cliente,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[Cliente]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM clientes ORDER BY apellido, nombre;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, cliente: Cliente) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                "UPDATE clientes SET nombre = ?, apellido = ?, dni = ?, telefono = ?, email = ? WHERE id = ?;",
                (cliente.nombre, cliente.apellido, cliente.dni, cliente.telefono, cliente.email, cliente.id),
            )
            conn.commit()

    def eliminar(self, id_cliente: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM clientes WHERE id = ?;", (id_cliente,))
            conn.commit()


class SQLiteMascotaRepositorio(IMascotaRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> Mascota:
        return Mascota(
            id_mascota=row["id"],
            id_cliente=row["id_cliente"],
            nombre=row["nombre"],
            especie=row["especie"],
            raza=row["raza"] or "Mestizo",
            edad=row["edad"],
            peso=row["peso"],
        )

    def guardar(self, mascota: Mascota) -> Mascota:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO mascotas (id_cliente, nombre, especie, raza, edad, peso) VALUES (?, ?, ?, ?, ?, ?);",
                (mascota.id_cliente, mascota.nombre, mascota.especie, mascota.raza, mascota.edad, mascota.peso),
            )
            conn.commit()
            mascota.id = cursor.lastrowid
        return mascota

    def obtener_por_id(self, id_mascota: int) -> Optional[Mascota]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM mascotas WHERE id = ?;", (id_mascota,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[Mascota]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM mascotas ORDER BY id DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def listar_por_cliente(self, id_cliente: int) -> List[Mascota]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM mascotas WHERE id_cliente = ?;", (id_cliente,)).fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, mascota: Mascota) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                "UPDATE mascotas SET id_cliente = ?, nombre = ?, especie = ?, raza = ?, edad = ?, peso = ? WHERE id = ?;",
                (mascota.id_cliente, mascota.nombre, mascota.especie, mascota.raza, mascota.edad, mascota.peso, mascota.id),
            )
            conn.commit()

    def eliminar(self, id_mascota: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM mascotas WHERE id = ?;", (id_mascota,))
            conn.commit()


class SQLiteTurnoRepositorio(ITurnoRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> Turno:
        return Turno(
            id_turno=row["id"],
            id_mascota=row["id_mascota"],
            veterinario=row["veterinario"],
            fecha_hora=_str_a_dt(row["fecha_hora"]),
            estado=row["estado"],
        )

    def guardar(self, turno: Turno) -> Turno:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO turnos (id_mascota, veterinario, fecha_hora, estado) VALUES (?, ?, ?, ?);",
                (turno.id_mascota, turno.veterinario, _dt_a_str(turno.fecha_hora), turno.estado),
            )
            conn.commit()
            turno.id = cursor.lastrowid
        return turno

    def obtener_por_id(self, id_turno: int) -> Optional[Turno]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM turnos WHERE id = ?;", (id_turno,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[Turno]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM turnos ORDER BY fecha_hora DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def listar_por_veterinario(self, veterinario: str) -> List[Turno]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM turnos WHERE LOWER(veterinario) = LOWER(?);",
                (veterinario.strip(),),
            ).fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, turno: Turno) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                "UPDATE turnos SET id_mascota = ?, veterinario = ?, fecha_hora = ?, estado = ? WHERE id = ?;",
                (turno.id_mascota, turno.veterinario, _dt_a_str(turno.fecha_hora), turno.estado, turno.id),
            )
            conn.commit()

    def eliminar(self, id_turno: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM turnos WHERE id = ?;", (id_turno,))
            conn.commit()


class SQLiteConsultaMedicaRepositorio(IConsultaMedicaRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> ConsultaMedica:
        vacunas_str = row["vacunas_aplicadas"] or ""
        vacunas = [v.strip() for v in vacunas_str.split(",") if v.strip()]
        return ConsultaMedica(
            id_consulta=row["id"],
            id_mascota=row["id_mascota"],
            fecha_hora=_str_a_dt(row["fecha_hora"]),
            motivo=row["motivo"],
            diagnostico=row["diagnostico"] or "",
            tratamiento=row["tratamiento"] or "",
            vacunas_aplicadas=vacunas,
            veterinario=row["veterinario"],
        )

    def guardar(self, consulta: ConsultaMedica) -> ConsultaMedica:
        vacunas_str = ",".join(consulta.vacunas_aplicadas)
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO consultas_medicas
                (id_mascota, fecha_hora, motivo, diagnostico, tratamiento, vacunas_aplicadas, veterinario)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    consulta.id_mascota,
                    _dt_a_str(consulta.fecha_hora),
                    consulta.motivo,
                    consulta.diagnostico,
                    consulta.tratamiento,
                    vacunas_str,
                    consulta.veterinario,
                ),
            )
            conn.commit()
            consulta.id = cursor.lastrowid
        return consulta

    def obtener_por_id(self, id_consulta: int) -> Optional[ConsultaMedica]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM consultas_medicas WHERE id = ?;", (id_consulta,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[ConsultaMedica]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM consultas_medicas ORDER BY fecha_hora DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def listar_por_mascota(self, id_mascota: int) -> List[ConsultaMedica]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM consultas_medicas WHERE id_mascota = ? ORDER BY fecha_hora ASC;",
                (id_mascota,),
            ).fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, consulta: ConsultaMedica) -> None:
        vacunas_str = ",".join(consulta.vacunas_aplicadas)
        with self._db.get_connection() as conn:
            conn.execute(
                """
                UPDATE consultas_medicas
                SET id_mascota = ?, fecha_hora = ?, motivo = ?, diagnostico = ?,
                    tratamiento = ?, vacunas_aplicadas = ?, veterinario = ?
                WHERE id = ?;
                """,
                (
                    consulta.id_mascota,
                    _dt_a_str(consulta.fecha_hora),
                    consulta.motivo,
                    consulta.diagnostico,
                    consulta.tratamiento,
                    vacunas_str,
                    consulta.veterinario,
                    consulta.id,
                ),
            )
            conn.commit()

    def eliminar(self, id_consulta: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM consultas_medicas WHERE id = ?;", (id_consulta,))
            conn.commit()


class SQLiteComprobanteRepositorio(IComprobanteRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> ComprobanteAtencion:
        return ComprobanteAtencion(
            id_comprobante=row["id"],
            id_consulta=row["id_consulta"],
            fecha=_str_a_dt(row["fecha"]),
            monto_base=row["monto_base"],
            estrategia=obtener_estrategia(row["tipo_tarifa"]),
            total=row["total"],
        )

    def guardar(self, comprobante: ComprobanteAtencion) -> ComprobanteAtencion:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO comprobantes_atencion (id_consulta, fecha, monto_base, tipo_tarifa, total)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    comprobante.id_consulta,
                    _dt_a_str(comprobante.fecha),
                    comprobante.monto_base,
                    comprobante.tipo_tarifa,
                    comprobante.total,
                ),
            )
            conn.commit()
            comprobante.id = cursor.lastrowid
        return comprobante

    def obtener_por_id(self, id_comprobante: int) -> Optional[ComprobanteAtencion]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM comprobantes_atencion WHERE id = ?;", (id_comprobante,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[ComprobanteAtencion]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM comprobantes_atencion ORDER BY id DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, comprobante: ComprobanteAtencion) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                """
                UPDATE comprobantes_atencion
                SET id_consulta = ?, fecha = ?, monto_base = ?, tipo_tarifa = ?, total = ?
                WHERE id = ?;
                """,
                (
                    comprobante.id_consulta,
                    _dt_a_str(comprobante.fecha),
                    comprobante.monto_base,
                    comprobante.tipo_tarifa,
                    comprobante.total,
                    comprobante.id,
                ),
            )
            conn.commit()

    def eliminar(self, id_comprobante: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM comprobantes_atencion WHERE id = ?;", (id_comprobante,))
            conn.commit()


class SQLiteOrdenDerivacionRepositorio(IOrdenDerivacionRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> OrdenDerivacion:
        return OrdenDerivacion(
            id_orden=row["id"],
            id_consulta=row["id_consulta"],
            id_mascota=row["id_mascota"],
            tipo_estudio=row["tipo_estudio"],
            diagnostico_presuntivo=row["diagnostico_presuntivo"] or "",
            fecha_emision=_str_a_dt(row["fecha_emision"]),
        )

    def guardar(self, orden: OrdenDerivacion) -> OrdenDerivacion:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO ordenes_derivacion
                (id_consulta, id_mascota, tipo_estudio, diagnostico_presuntivo, fecha_emision)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    orden.id_consulta,
                    orden.id_mascota,
                    orden.tipo_estudio,
                    orden.diagnostico_presuntivo,
                    _dt_a_str(orden.fecha_emision),
                ),
            )
            conn.commit()
            orden.id = cursor.lastrowid
        return orden

    def obtener_por_id(self, id_orden: int) -> Optional[OrdenDerivacion]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM ordenes_derivacion WHERE id = ?;", (id_orden,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[OrdenDerivacion]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM ordenes_derivacion ORDER BY id DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, orden: OrdenDerivacion) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                """
                UPDATE ordenes_derivacion
                SET id_consulta = ?, id_mascota = ?, tipo_estudio = ?, diagnostico_presuntivo = ?, fecha_emision = ?
                WHERE id = ?;
                """,
                (
                    orden.id_consulta,
                    orden.id_mascota,
                    orden.tipo_estudio,
                    orden.diagnostico_presuntivo,
                    _dt_a_str(orden.fecha_emision),
                    orden.id,
                ),
            )
            conn.commit()

    def eliminar(self, id_orden: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM ordenes_derivacion WHERE id = ?;", (id_orden,))
            conn.commit()


class SQLiteRemitoBiologicoRepositorio(IRemitoBiologicoRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> RemitoBiologico:
        return RemitoBiologico(
            id_remito=row["id"],
            codigo_remito=row["codigo_remito"],
            codigo_conservadora=row["codigo_conservadora"],
            temperatura_transporte=row["temperatura_transporte"],
            fecha_envio=_str_a_dt(row["fecha_envio"]),
            fecha_recepcion=_str_a_dt(row["fecha_recepcion"]),
            responsable_envio=row["responsable_envio"] or "",
            responsable_recepcion=row["responsable_recepcion"],
            estado=row["estado"],
        )

    def guardar(self, remito: RemitoBiologico) -> RemitoBiologico:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO remitos_biologicos
                (codigo_remito, codigo_conservadora, temperatura_transporte, fecha_envio,
                 fecha_recepcion, responsable_envio, responsable_recepcion, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    remito.codigo_remito,
                    remito.codigo_conservadora,
                    remito.temperatura_transporte,
                    _dt_a_str(remito.fecha_envio),
                    _dt_a_str(remito.fecha_recepcion),
                    remito.responsable_envio,
                    remito.responsable_recepcion,
                    remito.estado,
                ),
            )
            conn.commit()
            remito.id = cursor.lastrowid
        return remito

    def obtener_por_id(self, id_remito: int) -> Optional[RemitoBiologico]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM remitos_biologicos WHERE id = ?;", (id_remito,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[RemitoBiologico]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM remitos_biologicos ORDER BY id DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, remito: RemitoBiologico) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                """
                UPDATE remitos_biologicos
                SET codigo_remito = ?, codigo_conservadora = ?, temperatura_transporte = ?,
                    fecha_envio = ?, fecha_recepcion = ?, responsable_envio = ?,
                    responsable_recepcion = ?, estado = ?
                WHERE id = ?;
                """,
                (
                    remito.codigo_remito,
                    remito.codigo_conservadora,
                    remito.temperatura_transporte,
                    _dt_a_str(remito.fecha_envio),
                    _dt_a_str(remito.fecha_recepcion),
                    remito.responsable_envio,
                    remito.responsable_recepcion,
                    remito.estado,
                    remito.id,
                ),
            )
            conn.commit()

    def eliminar(self, id_remito: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM remitos_biologicos WHERE id = ?;", (id_remito,))
            conn.commit()


class SQLiteMuestraBiologicaRepositorio(IMuestraBiologicaRepositorio):
    def __init__(self, db_manager: DBManager) -> None:
        self._db = db_manager

    def _row_to_entity(self, row) -> MuestraBiologica:
        historial_str = row["historial_trazabilidad"] or ""
        historial = [linea for linea in historial_str.splitlines() if linea.strip()]
        return MuestraBiologica(
            id_muestra=row["id"],
            id_orden=row["id_orden"],
            id_remito=row["id_remito"],
            tipo_muestra=row["tipo_muestra"],
            codigo_precinto=row["codigo_precinto"],
            precinto_roto=bool(row["precinto_roto"]),
            estado=EstadoMuestra.desde_nombre(row["estado"]),
            historial_trazabilidad=historial,
            fecha_extraccion=_str_a_dt(row["fecha_extraccion"]),
            fecha_recepcion=_str_a_dt(row["fecha_recepcion"]),
            fecha_analisis=_str_a_dt(row["fecha_analisis"]),
            resultado=row["resultado"],
            motivo_rechazo=row["motivo_rechazo"],
        )

    def guardar(self, muestra: MuestraBiologica) -> MuestraBiologica:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO muestras_biologicas
                (id_orden, id_remito, tipo_muestra, codigo_precinto, precinto_roto, estado,
                 historial_trazabilidad, fecha_extraccion, fecha_recepcion, fecha_analisis, resultado, motivo_rechazo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    muestra.id_orden,
                    muestra.id_remito,
                    muestra.tipo_muestra,
                    muestra.codigo_precinto,
                    1 if muestra.precinto_roto else 0,
                    muestra.nombre_estado,
                    muestra.obtener_log_texto(),
                    _dt_a_str(muestra.fecha_extraccion),
                    _dt_a_str(muestra.fecha_recepcion),
                    _dt_a_str(muestra.fecha_analisis),
                    muestra.resultado,
                    muestra.motivo_rechazo,
                ),
            )
            conn.commit()
            muestra.id = cursor.lastrowid
        return muestra

    def obtener_por_id(self, id_muestra: int) -> Optional[MuestraBiologica]:
        with self._db.get_connection() as conn:
            row = conn.execute("SELECT * FROM muestras_biologicas WHERE id = ?;", (id_muestra,)).fetchone()
            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[MuestraBiologica]:
        with self._db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM muestras_biologicas ORDER BY id DESC;").fetchall()
            return [self._row_to_entity(r) for r in rows]

    def listar_por_remito(self, id_remito: int) -> List[MuestraBiologica]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM muestras_biologicas WHERE id_remito = ?;",
                (id_remito,),
            ).fetchall()
            return [self._row_to_entity(r) for r in rows]

    def listar_por_estado(self, nombre_estado: str) -> List[MuestraBiologica]:
        with self._db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM muestras_biologicas WHERE LOWER(estado) = LOWER(?);",
                (nombre_estado.strip(),),
            ).fetchall()
            return [self._row_to_entity(r) for r in rows]

    def actualizar(self, muestra: MuestraBiologica) -> None:
        with self._db.get_connection() as conn:
            conn.execute(
                """
                UPDATE muestras_biologicas
                SET id_orden = ?, id_remito = ?, tipo_muestra = ?, codigo_precinto = ?,
                    precinto_roto = ?, estado = ?, historial_trazabilidad = ?,
                    fecha_extraccion = ?, fecha_recepcion = ?, fecha_analisis = ?,
                    resultado = ?, motivo_rechazo = ?
                WHERE id = ?;
                """,
                (
                    muestra.id_orden,
                    muestra.id_remito,
                    muestra.tipo_muestra,
                    muestra.codigo_precinto,
                    1 if muestra.precinto_roto else 0,
                    muestra.nombre_estado,
                    muestra.obtener_log_texto(),
                    _dt_a_str(muestra.fecha_extraccion),
                    _dt_a_str(muestra.fecha_recepcion),
                    _dt_a_str(muestra.fecha_analisis),
                    muestra.resultado,
                    muestra.motivo_rechazo,
                    muestra.id,
                ),
            )
            conn.commit()

    def eliminar(self, id_muestra: int) -> None:
        with self._db.get_connection() as conn:
            conn.execute("DELETE FROM muestras_biologicas WHERE id = ?;", (id_muestra,))
            conn.commit()
