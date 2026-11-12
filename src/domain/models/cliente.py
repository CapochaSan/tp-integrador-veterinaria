from __future__ import annotations
from typing import Optional


class Cliente:
    """Entidad Cliente / Tutor responsable de las mascotas."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        dni: str,
        telefono: str = "",
        email: str = "",
        id_cliente: Optional[int] = None,
    ) -> None:
        self._id: Optional[int] = id_cliente
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.telefono = telefono
        self.email = email

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de cliente debe ser un entero positivo.")
        self._id = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El apellido del cliente no puede estar vacío.")
        self._apellido = valor.strip()

    @property
    def dni(self) -> str:
        return self._dni

    @dni.setter
    def dni(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El DNI del cliente no puede estar vacío.")
        self._dni = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self._telefono = (valor or "").strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        self._email = (valor or "").strip()

    @property
    def nombre_completo(self) -> str:
        return f"{self._apellido}, {self._nombre}"

    def __str__(self) -> str:
        return f"Cliente(ID: {self._id}, {self.nombre_completo}, DNI: {self._dni})"

    def __repr__(self) -> str:
        return self.__str__()
