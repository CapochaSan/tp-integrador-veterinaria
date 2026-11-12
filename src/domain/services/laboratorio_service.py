from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Tuple

from src.domain.models.orden_derivacion import OrdenDerivacion
from src.domain.models.remito_biologico import RemitoBiologico
from src.domain.models.muestra_biologica import MuestraBiologica
from src.domain.interfaces.repositorios import (
    IOrdenDerivacionRepositorio,
    IRemitoBiologicoRepositorio,
    IMuestraBiologicaRepositorio,
    IConsultaMedicaRepositorio,
    IMascotaRepositorio,
)


class LaboratorioService:
    """Servicio de aplicación para la gestión de derivaciones, remitos y muestras biológicas."""

    def __init__(
        self,
        orden_repo: IOrdenDerivacionRepositorio,
        remito_repo: IRemitoBiologicoRepositorio,
        muestra_repo: IMuestraBiologicaRepositorio,
        consulta_repo: IConsultaMedicaRepositorio,
        mascota_repo: IMascotaRepositorio,
    ) -> None:
        self._orden_repo = orden_repo
        self._remito_repo = remito_repo
        self._muestra_repo = muestra_repo
        self._consulta_repo = consulta_repo
        self._mascota_repo = mascota_repo

    def crear_orden_y_muestra(
        self,
        id_consulta: int,
        id_mascota: int,
        tipo_estudio: str,
        diagnostico_presuntivo: str,
        tipo_muestra: str,
        codigo_precinto: str,
    ) -> Tuple[OrdenDerivacion, MuestraBiologica]:
        if self._consulta_repo.obtener_por_id(id_consulta) is None:
            raise ValueError(f"No existe la consulta médica ID {id_consulta}.")
        if self._mascota_repo.obtener_por_id(id_mascota) is None:
            raise ValueError(f"No existe la mascota ID {id_mascota}.")

        orden = OrdenDerivacion(
            id_consulta=id_consulta,
            id_mascota=id_mascota,
            tipo_estudio=tipo_estudio,
            diagnostico_presuntivo=diagnostico_presuntivo,
        )
        orden_guardada = self._orden_repo.guardar(orden)

        muestra = MuestraBiologica(
            id_orden=orden_guardada.id,
            tipo_muestra=tipo_muestra,
            codigo_precinto=codigo_precinto,
        )
        muestra_guardada = self._muestra_repo.guardar(muestra)
        return orden_guardada, muestra_guardada

    def empaquetar_muestras(
        self,
        ids_muestras: List[int],
        codigo_remito: str,
        codigo_conservadora: str,
        temperatura_transporte: float = 4.0,
        responsable_envio: str = "Veterinario Clínica",
    ) -> RemitoBiologico:
        if not ids_muestras:
            raise ValueError("Debe seleccionar al menos una muestra para empaquetar.")

        muestras: List[MuestraBiologica] = []
        for id_m in ids_muestras:
            m = self._muestra_repo.obtener_por_id(id_m)
            if m is None:
                raise ValueError(f"No existe la muestra ID {id_m}.")
            if m.nombre_estado != "Extraída":
                raise ValueError(f"La muestra ID {id_m} está en estado '{m.nombre_estado}', solo pueden empaquetarse muestras 'Extraída'.")
            muestras.append(m)

        remito = RemitoBiologico(
            codigo_remito=codigo_remito,
            codigo_conservadora=codigo_conservadora,
            temperatura_transporte=temperatura_transporte,
            responsable_envio=responsable_envio,
            estado="Generado",
        )
        remito_guardado = self._remito_repo.guardar(remito)

        for m in muestras:
            m.empaquetar(id_remito=remito_guardado.id)
            self._muestra_repo.actualizar(m)

        return remito_guardado

    def despachar_remito(self, id_remito: int, responsable: str = "") -> RemitoBiologico:
        remito = self._remito_repo.obtener_por_id(id_remito)
        if remito is None:
            raise ValueError(f"No existe el remito ID {id_remito}.")
        if remito.estado != "Generado":
            raise ValueError(f"El remito ya se encuentra en estado '{remito.estado}'.")

        remito.despachar(responsable=responsable or remito.responsable_envio)
        self._remito_repo.actualizar(remito)

        muestras = self._muestra_repo.listar_por_remito(id_remito)
        for m in muestras:
            if m.nombre_estado == "Empaquetada":
                m.despachar()
                self._muestra_repo.actualizar(m)

        return remito

    def recibir_muestra(
        self, id_muestra: int, precinto_roto: bool, responsable_recepcion: str = "Técnico Lab"
    ) -> MuestraBiologica:
        muestra = self._muestra_repo.obtener_por_id(id_muestra)
        if muestra is None:
            raise ValueError(f"No existe la muestra ID {id_muestra}.")

        muestra.recibir(precinto_roto=precinto_roto)
        self._muestra_repo.actualizar(muestra)

        if muestra.id_remito is not None:
            remito = self._remito_repo.obtener_por_id(muestra.id_remito)
            if remito is not None and remito.estado == "En Tránsito":
                muestras_remito = self._muestra_repo.listar_por_remito(remito.id)
                todas_recibidas = all(
                    mr.nombre_estado in ("Recibida", "Rechazada", "Analizada")
                    for mr in muestras_remito
                )
                if todas_recibidas:
                    remito.recibir(responsable=responsable_recepcion)
                    self._remito_repo.actualizar(remito)

        return muestra

    def cargar_resultado_analisis(self, id_muestra: int, resultado: str) -> MuestraBiologica:
        muestra = self._muestra_repo.obtener_por_id(id_muestra)
        if muestra is None:
            raise ValueError(f"No existe la muestra ID {id_muestra}.")

        muestra.analizar(resultado)
        self._muestra_repo.actualizar(muestra)
        return muestra

    def rechazar_muestra_en_laboratorio(self, id_muestra: int, motivo: str) -> MuestraBiologica:
        muestra = self._muestra_repo.obtener_por_id(id_muestra)
        if muestra is None:
            raise ValueError(f"No existe la muestra ID {id_muestra}.")

        muestra.rechazar(motivo)
        self._muestra_repo.actualizar(muestra)
        return muestra

    def listar_ordenes(self) -> List[OrdenDerivacion]:
        return self._orden_repo.listar_todos()

    def listar_remitos(self) -> List[RemitoBiologico]:
        return self._remito_repo.listar_todos()

    def listar_muestras(self) -> List[MuestraBiologica]:
        return self._muestra_repo.listar_todos()
