from __future__ import annotations
from abc import ABC, abstractmethod


class EstrategiaFacturacion(ABC):
    """
    Clase abstracta base para el Patrón Strategy que calcula el monto final
    de un comprobante de atención clínica según la modalidad de atención.
    """

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre descriptivo de la tarifa."""
        pass

    @abstractmethod
    def calcular_total(self, monto_base: float) -> float:
        """Calcula el total a facturar a partir del monto base."""
        pass


class TarifaNormal(EstrategiaFacturacion):
    """Tarifa para consultas programadas en horario habitual."""

    @property
    def nombre(self) -> str:
        return "Normal"

    def calcular_total(self, monto_base: float) -> float:
        if monto_base < 0:
            raise ValueError("El monto base no puede ser negativo.")
        return round(float(monto_base), 2)


class TarifaUrgencia(EstrategiaFacturacion):
    """Tarifa para atenciones de urgencia o guardia (aplica 50% de recargo)."""

    RECARGO_URGENCIA = 0.50

    @property
    def nombre(self) -> str:
        return "Urgencia"

    def calcular_total(self, monto_base: float) -> float:
        if monto_base < 0:
            raise ValueError("El monto base no puede ser negativo.")
        total = monto_base * (1.0 + self.RECARGO_URGENCIA)
        return round(float(total), 2)


def obtener_estrategia(tipo: str) -> EstrategiaFacturacion:
    """Factory simple para instanciar la estrategia según el nombre."""
    tipo_norm = (tipo or "").strip().lower()
    if "urg" in tipo_norm:
        return TarifaUrgencia()
    return TarifaNormal()
