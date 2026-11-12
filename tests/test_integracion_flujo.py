import pytest

from src.domain.models.mascota import Mascota
from src.domain.models.consulta_medica import ConsultaMedica
from src.infrastructure.database.db_manager import DBManager
from src.infrastructure.repositories.sqlite_repositorios import (
    SQLiteClienteRepositorio,
    SQLiteMascotaRepositorio,
    SQLiteTurnoRepositorio,
    SQLiteConsultaMedicaRepositorio,
    SQLiteComprobanteRepositorio,
    SQLiteOrdenDerivacionRepositorio,
    SQLiteRemitoBiologicoRepositorio,
    SQLiteMuestraBiologicaRepositorio,
)
from src.infrastructure.reports.generador_pdf import GeneradorPDF
from src.domain.services.cliente_service import ClinicaService
from src.domain.services.laboratorio_service import LaboratorioService


def test_mascota_requiere_id_cliente_valido():
    with pytest.raises(ValueError, match="id_cliente"):
        Mascota(id_cliente=0, nombre="Firulais")

    with pytest.raises(ValueError, match="id_cliente"):
        Mascota(id_cliente=-1, nombre="Michi")


def test_control_esquema_vacunas_obligatorias():
    consulta_incompleta = ConsultaMedica(
        id_mascota=1,
        motivo="Control",
        diagnostico="Sano",
        tratamiento="Ninguno",
        veterinario="Dra. Ana López",
        vacunas_aplicadas=["Rabia"],
    )
    al_dia, pendientes = consulta_incompleta.controlar_esquema_vacunas(["Rabia", "Quíntuple", "Parvovirus"])
    assert al_dia is False
    assert pendientes == ["Quíntuple", "Parvovirus"]

    consulta_completa = ConsultaMedica(
        id_mascota=1,
        motivo="Refuerzo",
        diagnostico="Sano",
        tratamiento="Ninguno",
        veterinario="Dra. Ana López",
        vacunas_aplicadas=["Rabia", "Quíntuple", "Parvovirus"],
    )
    al_dia_ok, pendientes_ok = consulta_completa.controlar_esquema_vacunas(["Rabia", "Quíntuple", "Parvovirus"])
    assert al_dia_ok is True
    assert pendientes_ok == []


def test_seed_persistencia_servicios_y_cuatro_pdfs(tmp_path):
    db_file = tmp_path / "test_vet.db"
    pdf_dir = tmp_path / "pdfs"

    db_manager = DBManager(db_path=db_file)
    db_manager.inicializar_base_datos(cargar_seed=True)

    clinica_srv = ClinicaService(
        cliente_repo=SQLiteClienteRepositorio(db_manager),
        mascota_repo=SQLiteMascotaRepositorio(db_manager),
        turno_repo=SQLiteTurnoRepositorio(db_manager),
        consulta_repo=SQLiteConsultaMedicaRepositorio(db_manager),
        comprobante_repo=SQLiteComprobanteRepositorio(db_manager),
    )
    lab_srv = LaboratorioService(
        orden_repo=SQLiteOrdenDerivacionRepositorio(db_manager),
        remito_repo=SQLiteRemitoBiologicoRepositorio(db_manager),
        muestra_repo=SQLiteMuestraBiologicaRepositorio(db_manager),
        consulta_repo=SQLiteConsultaMedicaRepositorio(db_manager),
        mascota_repo=SQLiteMascotaRepositorio(db_manager),
    )

    # Verificar datos semilla cargados
    assert len(clinica_srv.listar_clientes()) >= 3
    assert len(clinica_srv.listar_mascotas()) >= 4
    assert len(lab_srv.listar_muestras()) >= 4

    # Verificar los 4 PDFs se generan sin errores y pesan > 0 bytes
    generador = GeneradorPDF(db_manager=db_manager, output_dir=pdf_dir)
    r1 = generador.generar_reporte_atenciones_y_derivaciones()
    r2 = generador.generar_reporte_muestras_rechazadas()
    r3 = generador.generar_reporte_tratamientos_y_vacunas()
    r4 = generador.generar_reporte_tiempos_muestras()

    for ruta in (r1, r2, r3, r4):
        assert ruta.exists()
        assert ruta.stat().st_size > 500
