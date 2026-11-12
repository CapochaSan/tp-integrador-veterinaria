from __future__ import annotations
from abc import ABC, abstractmethod


class EstrategiaFacturacion(ABC):
    #Clase abstracta base para el Patrón Strategy
    @property
    @abstractmethod
    def nombre(self) -> str:
        pass

    @abstractmethod
    def calcular_total(self, monto_base: float) -> float:
        pass


class TarifaNormal(EstrategiaFacturacion):
    # Clase concreta que hereda de EstrategiaFacturacion
    # El monto de la tarifa es simplemente el monto base

    @property
    def nombre(self) -> str:
        return "Normal"

    def calcular_total(self, monto_base: float) -> float:
        if monto_base < 0:
            raise ValueError("El monto base no puede ser negativo.")
        return round(float(monto_base), 2)


class TarifaUrgencia(EstrategiaFacturacion):
    # Clase concreta que hereda de EstrategiaFacturacion
    # Esta tarifa tiene un 50% de cargo, lo podemos configurar en la variable global de abajo

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
    # Factory para instanciar la estrategia según el nombre
    # Quien usa el metodo, no sabe exactamente que tipo de tarifa es, lo que espera es una EstrategiaFacturación
    tipo_norm = (tipo or "").strip().lower()
    if "urg" in tipo_norm:
        return TarifaUrgencia()
    return TarifaNormal()
