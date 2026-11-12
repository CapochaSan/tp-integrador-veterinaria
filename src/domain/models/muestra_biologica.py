class Muestra:
    def __init__(self, idMuestra, tipo, estado):
        self.id = idMuestra
        self.estado_actual = estado
        self.resultado_analisis = None
        self.tipo = tipo
        self.fecha_extracción = None
        self.remito = None
        self.motivo_rechazo = None
