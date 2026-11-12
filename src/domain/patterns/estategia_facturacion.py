# Alias por compatibilidad con el typo en la consigna/nombre previo
from src.domain.patterns.estrategia_facturacion import (
    EstrategiaFacturacion,
    TarifaNormal,
    TarifaUrgencia,
    obtener_estrategia,
)

__all__ = [
    "EstrategiaFacturacion",
    "TarifaNormal",
    "TarifaUrgencia",
    "obtener_estrategia",
]
