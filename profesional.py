class Profesional:
    def __init__(self, matricula, nombre, apellido, especialidad):
        self.matricula = matricula
        self.nombre = nombre
        self.apellido = apellido
        self.especialidad = especialidad


    def validar(self):
        "Devuelve un texto con el error si algo está mal, o None si está todo OK."
        if self.matricula == "" or self.nombre == "" or self.apellido == "" or self.especialidad == "":
            return "Todos los campos son obligatorios."
        if not self.matricula.isdigit():
            return "El número de matricula debe tener solo números."
        return None

    def __str__(self):
        return f"({self.matricula}, {self.nombre} - {self.apellido} {self.especialidad})"