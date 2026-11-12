from __future__ import annotations
from datetime import datetime
from typing import Optional


class OrdenDerivacion:
    """Entidad Orden de Derivación a Laboratorio Externo / Central."""

    def __init__(
        self,
        id_consulta: int,
        id_mascota: int,
        tipo_estudio: str,
        diagnostico_presuntivo: str = "",
        fecha_emision: Optional[datetime] = None,
        id_orden: Optional[int] = None,
    ) -> None:
        self._id: Optional[int] = id_orden
        self.id_consulta = id_consulta
        self.id_mascota = id_mascota
        self.tipo_estudio = tipo_estudio
        self.diagnostico_presuntivo = diagnostico_presuntivo
        self.fecha_emision = fecha_emision or datetime.now()

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de la orden debe ser un entero positivo.")
        self._id = valor

    @property
    def id_consulta(self) -> int:
        return self._id_consulta

    @id_consulta.setter
    def id_consulta(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("La orden debe estar asociada a una consulta válida.")
        self._id_consulta = valor

    @property
    def id_mascota(self) -> int:
        return self._id_mascota

    @id_mascota.setter
    def id_mascota(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("La orden debe estar asociada a una mascota válida.")
        self._id_mascota = valor

    @property
    def tipo_estudio(self) -> str:
        return self._tipo_estudio

    @tipo_estudio.setter
    def tipo_estudio(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("Debe especificarse el tipo de estudio a realizar.")
        self._tipo_estudio = valor.strip()

    @property
    def diagnostico_presuntivo(self) -> str:
        return self._diagnostico_presuntivo

    @diagnostico_presuntivo.setter
    def diagnostico_presuntivo(self, valor: str) -> None:
        self._diagnostico_presuntivo = (valor or "").strip()

    @property
    def fecha_emision(self) -> datetime:
        return self._fecha_emision

    @fecha_emision.setter
    def fecha_emision(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise TypeError("fecha_emision debe ser una instancia de datetime.")
        self._fecha_emision = valor

    def __str__(self) -> str:
        return (
            f"OrdenDerivacion(ID: {self._id}, Consulta ID: {self._id_consulta}, "
            f"Estudio: {self._tipo_estudio}, Emisión: {self._fecha_emision.strftime('%d/%m/%Y')})"
        )

    def __repr__(self) -> str:
        return self.__str__()
