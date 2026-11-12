from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Tuple


class ConsultaMedica:

    def __init__(
        self,
        id_mascota: int,
        motivo: str,
        diagnostico: str,
        tratamiento: str,
        veterinario: str,
        fecha_hora: Optional[datetime] = None,
        vacunas_aplicadas: Optional[List[str]] = None,
        id_consulta: Optional[int] = None,
    ) -> None:
        self._id: Optional[int] = id_consulta
        self.id_mascota = id_mascota
        self.fecha_hora = fecha_hora or datetime.now()
        self.motivo = motivo
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.veterinario = veterinario
        # Normalizamos las vacunas enviadas por parametro del constructor, le sacamos los espacios si la vacuna existe dentro de  vacunas aplicadas
        # y agregamos el or [] por si alguien manda un None
        self._vacunas_aplicadas: List[str] = [v.strip() for v in (vacunas_aplicadas or []) if v and v.strip()]

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de consulta debe ser un entero positivo.")
        self._id = valor

    @property
    def id_mascota(self) -> int:
        return self._id_mascota

    @id_mascota.setter
    def id_mascota(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("La consulta debe estar asociada a una mascota válida.")
        self._id_mascota = valor

    @property
    def fecha_hora(self) -> datetime:
        return self._fecha_hora

    @fecha_hora.setter
    def fecha_hora(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise TypeError("fecha_hora debe ser una instancia de datetime.")
        self._fecha_hora = valor

    @property
    def motivo(self) -> str:
        return self._motivo

    @motivo.setter
    def motivo(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El motivo de la consulta no puede estar vacío.")
        self._motivo = valor.strip()

    @property
    def diagnostico(self) -> str:
        return self._diagnostico

    @diagnostico.setter
    def diagnostico(self, valor: str) -> None:
        self._diagnostico = (valor or "").strip()

    @property
    def tratamiento(self) -> str:
        return self._tratamiento

    @tratamiento.setter
    def tratamiento(self, valor: str) -> None:
        self._tratamiento = (valor or "").strip()

    @property
    def veterinario(self) -> str:
        return self._veterinario

    @veterinario.setter
    def veterinario(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("Debe indicarse el veterinario actuante.")
        self._veterinario = valor.strip()

    @property
    def vacunas_aplicadas(self) -> List[str]:
        return list(self._vacunas_aplicadas)

    def agregar_vacuna(self, vacuna: str) -> None:
        v_limpia = (vacuna or "").strip()
        if v_limpia and v_limpia not in self._vacunas_aplicadas:
            self._vacunas_aplicadas.append(v_limpia)

    def controlar_esquema_vacunas(self, vacunas_obligatorias: List[str]) -> Tuple[bool, List[str]]:
        
        # Retorna(vacunas_al_dia: bool, vacunas_pendientes: List[str]).
        
        # Guardamos en un conjunto las vacunas aplicadas, normalizadas sin espacios y en minuscula
        aplicadas_normalizadas = {v.strip().lower() for v in self._vacunas_aplicadas}
        pendientes: List[str] = []
        
        for obligatoria in vacunas_obligatorias:
            if obligatoria.strip().lower() not in aplicadas_normalizadas:
                pendientes.append(obligatoria.strip())

        al_dia = len(pendientes) == 0
        return al_dia, pendientes

    def __str__(self) -> str:
        return (
            f"ConsultaMedica(ID: {self._id}, Mascota: {self._id_mascota}, "
            f"Fecha: {self._fecha_hora.strftime('%d/%m/%Y %H:%M')}, Motivo: {self._motivo})"
        )

    def __repr__(self) -> str:
        return self.__str__()
