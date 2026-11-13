from __future__ import annotations
from typing import Optional


class Mascota:
    ESPECIES_VALIDAS = ("Canino", "Felino", "Ave", "Otro")

    def __init__(
        self,
        id_cliente: int,
        nombre: str,
        especie: str = "Canino",
        raza: str = "Mestizo",
        edad: int = 1,
        peso: float = 0.0,
        id_mascota: Optional[int] = None,
    ) -> None:
        self._id: Optional[int] = id_mascota
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.peso = peso

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de la mascota debe ser un entero positivo.")
        self._id = valor

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: int) -> None:
        if valor is None or not isinstance(valor, int) or valor <= 0:
            raise ValueError("Toda mascota debe tener un id_cliente válido asociado (entero positivo).")
        self._id_cliente = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre de la mascota no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def especie(self) -> str:
        return self._especie

    @especie.setter
    def especie(self, valor: str) -> None:
        especie_limpia = (valor or "Canino").strip().capitalize()
        self._especie = especie_limpia

    @property
    def raza(self) -> str:
        return self._raza

    @raza.setter
    def raza(self, valor: str) -> None:
        self._raza = (valor or "Mestizo").strip()

    @property
    def edad(self) -> int:
        return self._edad

    @edad.setter
    def edad(self, valor: int) -> None:
        if valor is None or valor < 0:
            raise ValueError("La edad de la mascota no puede ser negativa.")
        self._edad = int(valor)

    @property
    def peso(self) -> float:
        return self._peso

    @peso.setter
    def peso(self, valor: float) -> None:
        if valor is None or valor < 0:
            raise ValueError("El peso de la mascota no puede ser negativo.")
        self._peso = round(float(valor), 2)

    def __str__(self) -> str:
        return f"Mascota(ID: {self._id}, Nombre: {self._nombre}, Especie: {self._especie}, Cliente ID: {self._id_cliente})"

    def __repr__(self) -> str:
        return self.__str__()
