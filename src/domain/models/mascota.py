from datetime import date
from typing import Optional, TYPE_CHECKING

class Mascota:
    def __init__(self, idMascota, nombre, especie, fecha_nac,raza):
        self.id_mascota = idMascota
        self.nombre = nombre
        self.especie = especie
        self.fecha_nacimiento = fecha_nac
        self.id_cliente = None
