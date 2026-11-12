from datetime import datetime
import pytest

from src.domain.models.turno import Turno


def test_superposicion_mismo_veterinario_misma_hora():
    fecha = datetime(2026, 11, 15, 10, 0)
    turno_existente = Turno(id_mascota=1, veterinario="Dra. Ana López", fecha_hora=fecha, id_turno=1)
    turno_nuevo = Turno(id_mascota=2, veterinario="Dra. Ana López", fecha_hora=fecha)

    assert turno_nuevo.se_superpone_con(turno_existente) is True
    with pytest.raises(ValueError, match="Superposición detectada"):
        turno_nuevo.validar_disponibilidad([turno_existente])


def test_superposicion_parcial_dentro_de_30_minutos():
    t1 = Turno(id_mascota=1, veterinario="Dr. Carlos Ruiz", fecha_hora=datetime(2026, 11, 15, 10, 0), id_turno=1)
    t2 = Turno(id_mascota=2, veterinario="Dr. Carlos Ruiz", fecha_hora=datetime(2026, 11, 15, 10, 15))

    assert t2.se_superpone_con(t1) is True
    with pytest.raises(ValueError):
        t2.validar_disponibilidad([t1])


def test_turnos_consecutivos_sin_superposicion():
    t1 = Turno(id_mascota=1, veterinario="Dra. Ana López", fecha_hora=datetime(2026, 11, 15, 10, 0), id_turno=1)
    t2 = Turno(id_mascota=2, veterinario="Dra. Ana López", fecha_hora=datetime(2026, 11, 15, 10, 30))

    assert t2.se_superpone_con(t1) is False
    t2.validar_disponibilidad([t1])


def test_mismo_horario_distinto_veterinario_permitido():
    fecha = datetime(2026, 11, 15, 11, 0)
    t1 = Turno(id_mascota=1, veterinario="Dra. Ana López", fecha_hora=fecha, id_turno=1)
    t2 = Turno(id_mascota=2, veterinario="Dr. Carlos Ruiz", fecha_hora=fecha)

    assert t2.se_superpone_con(t1) is False
    t2.validar_disponibilidad([t1])


def test_turno_cancelado_libera_agenda():
    fecha = datetime(2026, 11, 15, 12, 0)
    t1 = Turno(id_mascota=1, veterinario="Dra. Ana López", fecha_hora=fecha, id_turno=1)
    t1.cancelar()

    t2 = Turno(id_mascota=2, veterinario="Dra. Ana López", fecha_hora=fecha)
    assert t2.se_superpone_con(t1) is False
    t2.validar_disponibilidad([t1])
