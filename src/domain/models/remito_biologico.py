from __future__ import annotations
from datetime import datetime
from typing import Optional


class RemitoBiologico:
    
    ESTADOS_VALIDOS = ("Generado", "En Tránsito", "Entregado")

    def __init__(
        self,
        codigo_remito: str,
        codigo_conservadora: str,
        temperatura_transporte: float = 4.0,
        fecha_envio: Optional[datetime] = None,
        fecha_recepcion: Optional[datetime] = None,
        responsable_envio: str = "",
        responsable_recepcion: Optional[str] = None,
        estado: str = "Generado",
        id_remito: Optional[int] = None,) -> None:
        
        self._id: Optional[int] = id_remito
        self.codigo_remito = codigo_remito
        self.codigo_conservadora = codigo_conservadora
        self.temperatura_transporte = temperatura_transporte
        self._fecha_envio: Optional[datetime] = fecha_envio
        self._fecha_recepcion: Optional[datetime] = fecha_recepcion
        self.responsable_envio = responsable_envio
        self.responsable_recepcion = responsable_recepcion
        self.estado = estado

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID del remito debe ser un entero positivo.")
        self._id = valor

    @property
    def codigo_remito(self) -> str:
        return self._codigo_remito

    @codigo_remito.setter
    def codigo_remito(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El código de remito no puede estar vacío.")
        self._codigo_remito = valor.strip().upper()

    @property
    def codigo_conservadora(self) -> str:
        return self._codigo_conservadora

    @codigo_conservadora.setter
    def codigo_conservadora(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El código de la conservadora no puede estar vacío.")
        self._codigo_conservadora = valor.strip().upper()

    @property
    def temperatura_transporte(self) -> float:
        return self._temperatura_transporte

    @temperatura_transporte.setter
    def temperatura_transporte(self, valor: float) -> None:
        self._temperatura_transporte = round(float(valor), 2)

    @property
    def fecha_envio(self) -> Optional[datetime]:
        return self._fecha_envio

    @fecha_envio.setter
    def fecha_envio(self, valor: Optional[datetime]) -> None:
        self._fecha_envio = valor

    @property
    def fecha_recepcion(self) -> Optional[datetime]:
        return self._fecha_recepcion

    @fecha_recepcion.setter
    def fecha_recepcion(self, valor: Optional[datetime]) -> None:
        self._fecha_recepcion = valor

    @property
    def responsable_envio(self) -> str:
        return self._responsable_envio

    @responsable_envio.setter
    def responsable_envio(self, valor: str) -> None:
        self._responsable_envio = (valor or "").strip()

    @property
    def responsable_recepcion(self) -> Optional[str]:
        return self._responsable_recepcion

    @responsable_recepcion.setter
    def responsable_recepcion(self, valor: Optional[str]) -> None:
        self._responsable_recepcion = (valor or "").strip() if valor else None

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, valor: str) -> None:
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado de remito inválido. Debe ser uno de: {self.ESTADOS_VALIDOS}")
        self._estado = valor

    def despachar(self, responsable: str = "") -> None:
        self._fecha_envio = datetime.now()
        if responsable:
            self._responsable_envio = responsable.strip()
        self._estado = "En Tránsito"

    def recibir(self, responsable: str = "") -> None:
        self._fecha_recepcion = datetime.now()
        if responsable:
            self._responsable_recepcion = responsable.strip()
        self._estado = "Entregado"

    def __str__(self) -> str:
        return (
            f"RemitoBiologico(ID: {self._id}, Código: {self._codigo_remito}, "
            f"Conservadora: {self._codigo_conservadora}, Temp: {self._temperatura_transporte}°C, "
            f"Estado: {self._estado})"
        )

    def __repr__(self) -> str:
        return self.__str__()
