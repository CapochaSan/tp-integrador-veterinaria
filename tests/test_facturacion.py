import pytest

from src.domain.patterns.estrategia_facturacion import (
    TarifaNormal,
    TarifaUrgencia,
    obtener_estrategia,
)
from src.domain.models.comprobante import ComprobanteAtencion


def test_tarifa_normal():
    estrategia = TarifaNormal()
    assert estrategia.nombre == "Normal"
    assert estrategia.calcular_total(10000.0) == 10000.0


def test_tarifa_urgencia():
    estrategia = TarifaUrgencia()
    assert estrategia.nombre == "Urgencia"
    assert estrategia.calcular_total(10000.0) == 15000.0


def test_comprobante_aplica_estrategia_y_permite_cambio():
    comp = ComprobanteAtencion(
        id_consulta=1,
        monto_base=12000.0,
        estrategia=TarifaNormal(),
    )
    assert comp.tipo_tarifa == "Normal"
    assert comp.total == 12000.0

    # Cambio de estrategia en tiempo de ejecución
    comp.estrategia = TarifaUrgencia()
    assert comp.tipo_tarifa == "Urgencia"
    assert comp.total == 18000.0


def test_monto_negativo_lanza_error():
    with pytest.raises(ValueError):
        TarifaNormal().calcular_total(-100.0)

    with pytest.raises(ValueError):
        ComprobanteAtencion(id_consulta=1, monto_base=-50.0, estrategia=TarifaUrgencia())


def test_factory_estrategia():
    assert isinstance(obtener_estrategia("Normal"), TarifaNormal)
    assert isinstance(obtener_estrategia("Urgencia"), TarifaUrgencia)
