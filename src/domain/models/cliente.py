class Cliente:
    def __init__(self, tipo_dni, nro_dni, nombre, apellido, estado="Activo"):
        self.tipo_dni = tipo_dni
        self.nro_dni = nro_dni
        self.nombre = nombre
        self.apellido = apellido
        self.estado = estado


    def validar(self):
        "Devuelve un texto con el error si algo está mal, o None si está todo OK."
        if self.tipo_dni == "" or self.nro_dni == "" or self.nombre == "" or self.apellido == "":
            return "Todos los campos son obligatorios."
        if self.tipo_dni not in ("DNI", "LC", "LE", "CI", "PAS"):
            return "Tipo de documento inválido (usar DNI, LC, LE, CI o PAS)."
        return None

    def __str__(self):
        return f"({self.apellido}, {self.nombre} - {self.tipo_dni} {self.nro_dni} ({self.estado})"