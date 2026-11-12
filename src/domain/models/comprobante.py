from __future__ import annotations
from datetime import datetime
from typing import Optional
from src.domain.patterns.estrategia_facturacion import (
    EstrategiaFacturacion,
    TarifaNormal,
    obtener_estrategia,
)


class ComprobanteAtencion:
    """Entidad Comprobante de Atención Clínica."""

    def __init__(
        self,
        id_consulta: int,
        monto_base: float,
        estrategia: Optional[EstrategiaFacturacion] = None,
        tipo_tarifa: Optional[str] = None,
        fecha: Optional[datetime] = None,
        total: Optional[float] = None,
        id_comprobante: Optional[int] = None,
    ) -> None:
        self._id: Optional[int] = id_comprobante
        self.id_consulta = id_consulta
        self.monto_base = monto_base
        self.fecha = fecha or datetime.now()

        if estrategia is not None:
            self._estrategia = estrategia
        elif tipo_tarifa is not None:
            self._estrategia = obtener_estrategia(tipo_tarifa)
        else:
            self._estrategia = TarifaNormal()

        if total is not None:
            self._total = round(float(total), 2)
        else:
            self._total = self._estrategia.calcular_total(self._monto_base)

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID del comprobante debe ser un entero positivo.")
        self._id = valor

    @property
    def id_consulta(self) -> int:
        return self._id_consulta

    @id_consulta.setter
    def id_consulta(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("El comprobante debe estar vinculado a una consulta válida.")
        self._id_consulta = valor

    @property
    def monto_base(self) -> float:
        return self._monto_base

    @monto_base.setter
    def monto_base(self, valor: float) -> None:
        if valor is None or valor < 0:
            raise ValueError("El monto base no puede ser negativo.")
        self._monto_base = round(float(valor), 2)

    @property
    def fecha(self) -> datetime:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise TypeError("fecha debe ser una instancia de datetime.")
        self._fecha = valor

    @property
    def estrategia(self) -> EstrategiaFacturacion:
        return self._estrategia

    @estrategia.setter
    def estrategia(self, valor: EstrategiaFacturacion) -> None:
        if not isinstance(valor, EstrategiaFacturacion):
            raise TypeError("La estrategia debe heredar de EstrategiaFacturacion.")
        self._estrategia = valor
        self.recalcular_total()

    @property
    def tipo_tarifa(self) -> str:
        return self._estrategia.nombre

    @property
    def total(self) -> float:
        return self._total

    def recalcular_total(self) -> float:
        """Aplica la estrategia seleccionada sobre el monto base."""
        self._total = self._estrategia.calcular_total(self._monto_base)
        return self._total

    def __str__(self) -> str:
        return (
            f"ComprobanteAtencion(ID: {self._id}, Consulta ID: {self._id_consulta}, "
            f"Tarifa: {self.tipo_tarifa}, Base: ${self._monto_base:.2f}, Total: ${self._total:.2f})"
        )

    def __repr__(self) -> str:
        return self.__str__()
