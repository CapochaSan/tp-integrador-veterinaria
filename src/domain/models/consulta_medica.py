class ConsultaMedica:
    def __init__(self, idConsulta, fecha, diagnostico, motivo):
        self.id = idConsulta
        self.fecha = fecha
        self.diagnostico = diagnostico
        self.motivo = motivo
        self.orden_derivacion = None