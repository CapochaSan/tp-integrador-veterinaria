import pytest

from src.domain.models.muestra_biologica import MuestraBiologica
from src.domain.patterns.estado_muestra import (
    EstadoExtraida,
    EstadoEmpaquetada,
    EstadoEnTransito,
    EstadoRecibida,
    EstadoAnalizada,
    EstadoRechazada,
)


def test_ciclo_completo_muestra_exitoso():
    muestra = MuestraBiologica(
        id_orden=1,
        tipo_muestra="Sangre EDTA",
        codigo_precinto="PREC-001",
    )
    assert isinstance(muestra.estado, EstadoExtraida)
    assert muestra.nombre_estado == "Extraída"

    muestra.empaquetar(id_remito=10)
    assert isinstance(muestra.estado, EstadoEmpaquetada)
    assert muestra.id_remito == 10

    muestra.despachar()
    assert isinstance(muestra.estado, EstadoEnTransito)

    muestra.recibir(precinto_roto=False)
    assert isinstance(muestra.estado, EstadoRecibida)
    assert muestra.precinto_roto is False
    assert muestra.fecha_recepcion is not None

    muestra.analizar("Hemograma dentro de valores normales")
    assert isinstance(muestra.estado, EstadoAnalizada)
    assert muestra.resultado == "Hemograma dentro de valores normales"
    assert muestra.fecha_analisis is not None

    # Verificar trazabilidad inmutable con timestamps
    log = muestra.historial_trazabilidad
    assert isinstance(log, tuple)
    assert len(log) == 5
    assert "Extraída" in log[0]
    assert "Empaquetada" in log[1]
    assert "En Tránsito" in log[2]
    assert "Recibida" in log[3]
    assert "Analizada" in log[4]


def test_rechazo_automatico_por_precinto_roto_y_bloqueo_analisis():
    muestra = MuestraBiologica(
        id_orden=2,
        tipo_muestra="Orina estéril",
        codigo_precinto="PREC-002",
    )
    muestra.empaquetar(id_remito=11)
    muestra.despachar()

    # Recepción con precinto roto == True -> pasa automáticamente a EstadoRechazada
    muestra.recibir(precinto_roto=True)
    assert isinstance(muestra.estado, EstadoRechazada)
    assert muestra.nombre_estado == "Rechazada"
    assert muestra.precinto_roto is True
    assert "precinto" in (muestra.motivo_rechazo or "").lower()

    # Debe bloquearse el análisis sobre una muestra rechazada
    with pytest.raises(ValueError, match="Rechazada"):
        muestra.analizar("Intento inválido de cargar resultado")


def test_transiciones_invalidas_lanzan_error():
    muestra = MuestraBiologica(
        id_orden=3,
        tipo_muestra="Suero",
        codigo_precinto="PREC-003",
    )

    # No se puede despachar sin empaquetar
    with pytest.raises(ValueError):
        muestra.despachar()

    # No se puede recibir sin haber despachado
    with pytest.raises(ValueError):
        muestra.recibir(precinto_roto=False)

    # No se puede analizar directamente desde Extraída
    with pytest.raises(ValueError):
        muestra.analizar("Resultado prematuro")
