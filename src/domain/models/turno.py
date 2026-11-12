from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, List


class Turno:

    ESTADOS_VALIDOS = ("Pendiente", "Atendido", "Cancelado")
    DURACION_ESTANDAR_MINUTOS = 30

    def __init__(
        self,
        id_mascota: int,
        veterinario: str,
        fecha_hora: datetime,
        estado: str = "Pendiente",
        id_turno: Optional[int] = None,) -> None:
        
        # El id del turno es "Optional" para que el constructor pueda funcionar cuando creamos un objeto
        # desde la interfaz porque aun no tiene id, cuando lo guardamos con repositorio.guardar(turno), el sqlite
        # le asigna un id. Cuando necesitamos reconstruir el objeto desde la BD, el objeto ya tiene un id
        
        self._id: Optional[int] = id_turno
        self.id_mascota = id_mascota
        self.veterinario = veterinario
        self.fecha_hora = fecha_hora
        self.estado = estado

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID del turno debe ser un entero positivo.")
        self._id = valor

    @property
    def id_mascota(self) -> int:
        return self._id_mascota

    @id_mascota.setter
    def id_mascota(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("El turno debe estar asociado a una mascota válida.")
        self._id_mascota = valor

    @property
    def veterinario(self) -> str:
        return self._veterinario

    @veterinario.setter
    def veterinario(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("Debe especificar el nombre del veterinario.")
        self._veterinario = valor.strip()

    @property
    def fecha_hora(self) -> datetime:
        return self._fecha_hora

    @fecha_hora.setter
    def fecha_hora(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise TypeError("fecha_hora debe ser una instancia de datetime.")
        self._fecha_hora = valor

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, valor: str) -> None:
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Debe ser uno de: {self.ESTADOS_VALIDOS}")
        self._estado = valor

    def se_superpone_con(self, otro: Turno) -> bool:
        # Verifica si el turno se solapa con otro del mismo veterinario con 30 min de ventana
        
        # Si el estado de alguno de los turnos es cancelado, no hay solapamiento
        if self._estado == "Cancelado" or otro.estado == "Cancelado":
            return False

        # Si es el mismo turno (ej. al editarse), no hay superposición consigo mismo
        if self._id is not None and otro.id is not None and self._id == otro.id:
            return False

        # Verificamos los vererinarios, solo se solapa cuando es el mismo veterinario
        if self._veterinario.lower() != otro.veterinario.lower():
            return False

        # El timedelta básicamente representa un intervalo de tiempo, en este caso la ventana de 30min
        
        fin_propio = self._fecha_hora + timedelta(minutes=self.DURACION_ESTANDAR_MINUTOS)
        fin_otro = otro.fecha_hora + timedelta(minutes=self.DURACION_ESTANDAR_MINUTOS)

        return (self._fecha_hora < fin_otro) and (otro.fecha_hora < fin_propio)

    def validar_disponibilidad(self, turnos_existentes: List[Turno]) -> None:
        # Recorremos todos los turnos para ver si el propio se superpone con alguno
        for existente in turnos_existentes:
            if self.se_superpone_con(existente):
                raise ValueError(
                    f"Superposición detectada: el Dr/a. {self._veterinario} ya tiene "
                    f"un turno asignado el {existente.fecha_hora.strftime('%d/%m/%Y %H:%M')}.")

    # Cambios de estado (no tiene patron state aplicado)
    def cancelar(self) -> None:
        if self._estado == "Atendido":
            raise ValueError("No se puede cancelar un turno que ya fue atendido.")
        self._estado = "Cancelado"

    def marcar_atendido(self) -> None:
        if self._estado == "Cancelado":
            raise ValueError("No se puede atender un turno cancelado.")
        self._estado = "Atendido"

    def __str__(self) -> str:
        return (
            f"Turno(ID: {self._id}, Mascota ID: {self._id_mascota}, "
            f"Vet: {self._veterinario}, Fecha: {self._fecha_hora.strftime('%d/%m/%Y %H:%M')}, "
            f"Estado: {self._estado})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Turno):
            return False
        # Si los id son None, todavía no se guardó en la BD
        if self._id is not None and otro._id is not None:
            return self._id == otro._id
        return (
            self._id_mascota == otro._id_mascota
            and self._veterinario.lower() == otro._veterinario.lower()
            and self._fecha_hora == otro._fecha_hora)
