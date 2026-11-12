from cliente import Cliente


class Mascota:
    def __init__(self, nombre, especie, cliente: Cliente):
        self.nombre = nombre
        self.especie = especie
        self.cliente = cliente

    def validar(self):
        """Devuelve un mensaje de error si faltan datos, o None si está todo OK."""
        if not self.nombre or not self.especie or self.cliente is None:
            return "El nombre, la especie y el cliente son obligatorios."
        return None

    def __str__(self):
        return f"{self.nombre} ({self.especie}) - Cliente: {self.cliente}"