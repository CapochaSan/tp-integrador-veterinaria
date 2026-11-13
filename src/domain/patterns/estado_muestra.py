from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.domain.models.muestra_biologica import MuestraBiologica


class EstadoMuestra(ABC):
    
    # Clase abstracta base para el Patrón State que modela el ciclo de vida
    # de una muestra biológica.
    
    @property
    @abstractmethod
    def nombre(self) -> str:
        pass
    
    # Los métodos por defecto devuelven None y dan error, cada clase concreta sobreescribe el método que utiliza
    def empaquetar(self, muestra: MuestraBiologica) -> None:
        raise ValueError(f"No se puede empaquetar una muestra en estado '{self.nombre}'.")

    def despachar(self, muestra: MuestraBiologica) -> None:
        raise ValueError(f"No se puede despachar a tránsito una muestra en estado '{self.nombre}'.")

    def recibir(self, muestra: MuestraBiologica, precinto_roto: bool = False) -> None:
        raise ValueError(f"No se puede recibir una muestra en estado '{self.nombre}'.")

    def analizar(self, muestra: MuestraBiologica, resultado: str) -> None:
        raise ValueError(f"No se puede analizar una muestra en estado '{self.nombre}'.")

    def rechazar(self, muestra: MuestraBiologica, motivo: str) -> None:
        raise ValueError(f"No se puede rechazar una muestra en estado '{self.nombre}'.")

    def __str__(self) -> str:
        return self.nombre

    def __eq__(self, otro: object) -> bool:
        if isinstance(otro, EstadoMuestra):
            return self.nombre == otro.nombre
        if isinstance(otro, str):
            return self.nombre.lower() == otro.lower()
        return False

    @staticmethod
    def desde_nombre(nombre: str) -> "EstadoMuestra":
        # Factory para reconstruir el estado a partir de su nombre persistido.
        nombre_normalizado = (nombre or "").strip().lower()
        if "extra" in nombre_normalizado:
            return EstadoExtraida()
        elif "empaquetad" in nombre_normalizado:
            return EstadoEmpaquetada()
        elif "transito" in nombre_normalizado or "tránsito" in nombre_normalizado:
            return EstadoEnTransito()
        elif "recibid" in nombre_normalizado:
            return EstadoRecibida()
        elif "analizad" in nombre_normalizado:
            return EstadoAnalizada()
        elif "rechazad" in nombre_normalizado:
            return EstadoRechazada()
        return EstadoExtraida()


class EstadoExtraida(EstadoMuestra):
    # Estado inicial: muestra tomada al paciente en la clínica.

    @property
    def nombre(self) -> str:
        return "Extraída"

    def empaquetar(self, muestra: MuestraBiologica) -> None:
        muestra._cambiar_estado(EstadoEmpaquetada(), "Muestra acondicionada y empaquetada en conservadora.")


class EstadoEmpaquetada(EstadoMuestra):
    # La muestra está guardada en la conservadora con precinto asignado.

    @property
    def nombre(self) -> str:
        return "Empaquetada"

    def despachar(self, muestra: MuestraBiologica) -> None:
        muestra._cambiar_estado(EstadoEnTransito(), "Conservadora despachada en remito hacia el laboratorio.")


class EstadoEnTransito(EstadoMuestra):
    # La muestra se encuentra en viaje hacia el laboratorio central.

    @property
    def nombre(self) -> str:
        return "En Tránsito"

    def recibir(self, muestra: MuestraBiologica, precinto_roto: bool = False) -> None:
        if precinto_roto:
            muestra._precinto_roto = True
            motivo = "Rechazo automático en recepción: Precinto de seguridad violado/roto durante el transporte."
            muestra._motivo_rechazo = motivo
            muestra._cambiar_estado(EstadoRechazada(), motivo)
        else:
            muestra._precinto_roto = False
            muestra._cambiar_estado(EstadoRecibida(), "Muestra recibida correctamente con precinto intacto.")


class EstadoRecibida(EstadoMuestra):
    # La muestra ingresó al laboratorio y está lista para su procesamiento.

    @property
    def nombre(self) -> str:
        return "Recibida"

    def analizar(self, muestra: MuestraBiologica, resultado: str) -> None:
        if not resultado or not resultado.strip():
            raise ValueError("Debe ingresar un resultado de análisis válido.")
        muestra._resultado = resultado.strip()
        muestra._cambiar_estado(EstadoAnalizada(), f"Análisis finalizado con éxito. Resultado: {muestra._resultado}")

    def rechazar(self, muestra: MuestraBiologica, motivo: str) -> None:
        if not motivo or not motivo.strip():
            motivo = "Muestra no apta para procesamiento técnico."
        muestra._motivo_rechazo = motivo.strip()
        muestra._cambiar_estado(EstadoRechazada(), f"Rechazo en laboratorio: {muestra._motivo_rechazo}")


class EstadoAnalizada(EstadoMuestra):
    # Estado final: la muestra fue analizada con resultados disponibles.

    @property
    def nombre(self) -> str:
        return "Analizada"


class EstadoRechazada(EstadoMuestra):
    # Estado final: la muestra fue rechazada (análisis bloqueado permanentemente).

    @property
    def nombre(self) -> str:
        return "Rechazada"

    def analizar(self, muestra: MuestraBiologica, resultado: str) -> None:
        raise ValueError("Operación bloqueada: No se puede analizar una muestra en estado Rechazada.")
