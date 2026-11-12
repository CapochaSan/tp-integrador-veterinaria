# La función de este archivo es exponer las interfaces abstractas públicas que otros archivos van a utilizar

from src.domain.interfaces.repositorios import (
    IClienteRepositorio,
    IMascotaRepositorio,
    ITurnoRepositorio,
    IConsultaMedicaRepositorio,
    IComprobanteRepositorio,
    IOrdenDerivacionRepositorio,
    IRemitoBiologicoRepositorio,
    IMuestraBiologicaRepositorio,
)

__all__ = [
    "IClienteRepositorio",
    "IMascotaRepositorio",
    "ITurnoRepositorio",
    "IConsultaMedicaRepositorio",
    "IComprobanteRepositorio",
    "IOrdenDerivacionRepositorio",
    "IRemitoBiologicoRepositorio",
    "IMuestraBiologicaRepositorio",
]
