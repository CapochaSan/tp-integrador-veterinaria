from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.cliente import Cliente
from src.domain.models.mascota import Mascota
from src.domain.models.turno import Turno
from src.domain.models.consulta_medica import ConsultaMedica
from src.domain.models.comprobante import ComprobanteAtencion
from src.domain.models.orden_derivacion import OrdenDerivacion
from src.domain.models.remito_biologico import RemitoBiologico
from src.domain.models.muestra_biologica import MuestraBiologica


class IClienteRepositorio(ABC):
    @abstractmethod
    def guardar(self, cliente: Cliente) -> Cliente:
        pass

    @abstractmethod
    def obtener_por_id(self, id_cliente: int) -> Optional[Cliente]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Cliente]:
        pass

    @abstractmethod
    def actualizar(self, cliente: Cliente) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_cliente: int) -> None:
        pass


class IMascotaRepositorio(ABC):
    @abstractmethod
    def guardar(self, mascota: Mascota) -> Mascota:
        pass

    @abstractmethod
    def obtener_por_id(self, id_mascota: int) -> Optional[Mascota]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Mascota]:
        pass

    @abstractmethod
    def listar_por_cliente(self, id_cliente: int) -> List[Mascota]:
        pass

    @abstractmethod
    def actualizar(self, mascota: Mascota) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_mascota: int) -> None:
        pass


class ITurnoRepositorio(ABC):
    @abstractmethod
    def guardar(self, turno: Turno) -> Turno:
        pass

    @abstractmethod
    def obtener_por_id(self, id_turno: int) -> Optional[Turno]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Turno]:
        pass

    @abstractmethod
    def listar_por_veterinario(self, veterinario: str) -> List[Turno]:
        pass

    @abstractmethod
    def actualizar(self, turno: Turno) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_turno: int) -> None:
        pass


class IConsultaMedicaRepositorio(ABC):
    @abstractmethod
    def guardar(self, consulta: ConsultaMedica) -> ConsultaMedica:
        pass

    @abstractmethod
    def obtener_por_id(self, id_consulta: int) -> Optional[ConsultaMedica]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[ConsultaMedica]:
        pass

    @abstractmethod
    def listar_por_mascota(self, id_mascota: int) -> List[ConsultaMedica]:
        pass

    @abstractmethod
    def actualizar(self, consulta: ConsultaMedica) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_consulta: int) -> None:
        pass


class IComprobanteRepositorio(ABC):
    @abstractmethod
    def guardar(self, comprobante: ComprobanteAtencion) -> ComprobanteAtencion:
        pass

    @abstractmethod
    def obtener_por_id(self, id_comprobante: int) -> Optional[ComprobanteAtencion]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[ComprobanteAtencion]:
        pass

    @abstractmethod
    def actualizar(self, comprobante: ComprobanteAtencion) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_comprobante: int) -> None:
        pass


class IOrdenDerivacionRepositorio(ABC):
    @abstractmethod
    def guardar(self, orden: OrdenDerivacion) -> OrdenDerivacion:
        pass

    @abstractmethod
    def obtener_por_id(self, id_orden: int) -> Optional[OrdenDerivacion]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[OrdenDerivacion]:
        pass

    @abstractmethod
    def actualizar(self, orden: OrdenDerivacion) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_orden: int) -> None:
        pass


class IRemitoBiologicoRepositorio(ABC):
    @abstractmethod
    def guardar(self, remito: RemitoBiologico) -> RemitoBiologico:
        pass

    @abstractmethod
    def obtener_por_id(self, id_remito: int) -> Optional[RemitoBiologico]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[RemitoBiologico]:
        pass

    @abstractmethod
    def actualizar(self, remito: RemitoBiologico) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_remito: int) -> None:
        pass


class IMuestraBiologicaRepositorio(ABC):
    @abstractmethod
    def guardar(self, muestra: MuestraBiologica) -> MuestraBiologica:
        pass

    @abstractmethod
    def obtener_por_id(self, id_muestra: int) -> Optional[MuestraBiologica]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[MuestraBiologica]:
        pass

    @abstractmethod
    def listar_por_remito(self, id_remito: int) -> List[MuestraBiologica]:
        pass

    @abstractmethod
    def listar_por_estado(self, nombre_estado: str) -> List[MuestraBiologica]:
        pass

    @abstractmethod
    def actualizar(self, muestra: MuestraBiologica) -> None:
        pass

    @abstractmethod
    def eliminar(self, id_muestra: int) -> None:
        pass
