from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Tuple
from src.domain.patterns.estado_muestra import (
    EstadoMuestra,
    EstadoExtraida,
    EstadoRecibida,
    EstadoRechazada,
    EstadoAnalizada,
)


class MuestraBiologica:
    """
    Entidad Muestra Biológica con ciclo de vida administrado por el Patrón State
    y registro de trazabilidad inmutable con timestamps.
    """

    def __init__(
        self,
        id_orden: int,
        tipo_muestra: str,
        codigo_precinto: str,
        precinto_roto: bool = False,
        estado: Optional[EstadoMuestra] = None,
        id_remito: Optional[int] = None,
        historial_trazabilidad: Optional[List[str]] = None,
        fecha_extraccion: Optional[datetime] = None,
        fecha_recepcion: Optional[datetime] = None,
        fecha_analisis: Optional[datetime] = None,
        resultado: Optional[str] = None,
        motivo_rechazo: Optional[str] = None,
        id_muestra: Optional[int] = None,
    ) -> None:
        self._id: Optional[int] = id_muestra
        self.id_orden = id_orden
        self._id_remito: Optional[int] = id_remito
        self.tipo_muestra = tipo_muestra
        self.codigo_precinto = codigo_precinto
        self._precinto_roto: bool = bool(precinto_roto)
        self._estado: EstadoMuestra = estado if estado is not None else EstadoExtraida()
        self._fecha_extraccion: datetime = fecha_extraccion or datetime.now()
        self._fecha_recepcion: Optional[datetime] = fecha_recepcion
        self._fecha_analisis: Optional[datetime] = fecha_analisis
        self._resultado: Optional[str] = resultado
        self._motivo_rechazo: Optional[str] = motivo_rechazo

        if historial_trazabilidad is not None and len(historial_trazabilidad) > 0:
            self._historial_trazabilidad: List[str] = list(historial_trazabilidad)
        else:
            ts = self._fecha_extraccion.strftime("%Y-%m-%d %H:%M:%S")
            self._historial_trazabilidad = [
                f"[{ts}] Estado -> {self._estado.nombre}: Muestra extraída (Precinto: {self._codigo_precinto}, Tipo: {self._tipo_muestra})."
            ]

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de la muestra debe ser un entero positivo.")
        self._id = valor

    @property
    def id_orden(self) -> int:
        return self._id_orden

    @id_orden.setter
    def id_orden(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("La muestra debe estar asociada a una orden de derivación válida.")
        self._id_orden = valor

    @property
    def id_remito(self) -> Optional[int]:
        return self._id_remito

    @id_remito.setter
    def id_remito(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de remito debe ser un entero positivo.")
        self._id_remito = valor

    @property
    def tipo_muestra(self) -> str:
        return self._tipo_muestra

    @tipo_muestra.setter
    def tipo_muestra(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El tipo de muestra no puede estar vacío.")
        self._tipo_muestra = valor.strip()

    @property
    def codigo_precinto(self) -> str:
        return self._codigo_precinto

    @codigo_precinto.setter
    def codigo_precinto(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El código de precinto sanitario no puede estar vacío.")
        self._codigo_precinto = valor.strip().upper()

    @property
    def precinto_roto(self) -> bool:
        return self._precinto_roto

    @property
    def estado(self) -> EstadoMuestra:
        return self._estado

    @property
    def nombre_estado(self) -> str:
        return self._estado.nombre

    @property
    def historial_trazabilidad(self) -> Tuple[str, ...]:
        """Retorna una tupla inmutable con el historial de eventos."""
        return tuple(self._historial_trazabilidad)

    @property
    def fecha_extraccion(self) -> datetime:
        return self._fecha_extraccion

    @property
    def fecha_recepcion(self) -> Optional[datetime]:
        return self._fecha_recepcion

    @fecha_recepcion.setter
    def fecha_recepcion(self, valor: Optional[datetime]) -> None:
        self._fecha_recepcion = valor

    @property
    def fecha_analisis(self) -> Optional[datetime]:
        return self._fecha_analisis

    @fecha_analisis.setter
    def fecha_analisis(self, valor: Optional[datetime]) -> None:
        self._fecha_analisis = valor

    @property
    def resultado(self) -> Optional[str]:
        return self._resultado

    @property
    def motivo_rechazo(self) -> Optional[str]:
        return self._motivo_rechazo

    def _cambiar_estado(self, nuevo_estado: EstadoMuestra, detalle: str) -> None:
        """
        Método interno invocado por las clases de EstadoMuestra para realizar
        la transición de estado y registrar la entrada inmutable en el log.
        """
        ahora = datetime.now()
        self._estado = nuevo_estado

        if isinstance(nuevo_estado, (EstadoRecibida, EstadoRechazada)) and self._fecha_recepcion is None:
            self._fecha_recepcion = ahora
        if isinstance(nuevo_estado, EstadoAnalizada) and self._fecha_analisis is None:
            self._fecha_analisis = ahora

        ts = ahora.strftime("%Y-%m-%d %H:%M:%S")
        self._historial_trazabilidad.append(
            f"[{ts}] Estado -> {nuevo_estado.nombre}: {detalle}"
        )

    def empaquetar(self, id_remito: Optional[int] = None) -> None:
        if id_remito is not None:
            self.id_remito = id_remito
        self._estado.empaquetar(self)

    def despachar(self) -> None:
        self._estado.despachar(self)

    def recibir(self, precinto_roto: bool = False) -> None:
        self._estado.recibir(self, precinto_roto)

    def analizar(self, resultado: str) -> None:
        self._estado.analizar(self, resultado)

    def rechazar(self, motivo: str) -> None:
        self._estado.rechazar(self, motivo)

    def obtener_log_texto(self) -> str:
        """Devuelve el log completo de trazabilidad en formato texto multilínea."""
        return "\n".join(self._historial_trazabilidad)

    def __str__(self) -> str:
        return (
            f"MuestraBiologica(ID: {self._id}, Orden: {self._id_orden}, "
            f"Tipo: {self._tipo_muestra}, Precinto: {self._codigo_precinto}, "
            f"Estado: {self._estado.nombre})"
        )

    def __repr__(self) -> str:
        return self.__str__()
