from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from config import VACUNAS_OBLIGATORIAS
from src.domain.models.cliente import Cliente
from src.domain.models.mascota import Mascota
from src.domain.models.turno import Turno
from src.domain.models.consulta_medica import ConsultaMedica
from src.domain.models.comprobante import ComprobanteAtencion
from src.domain.patterns.estrategia_facturacion import obtener_estrategia
from src.domain.interfaces.repositorios import (
    IClienteRepositorio,
    IMascotaRepositorio,
    ITurnoRepositorio,
    IConsultaMedicaRepositorio,
    IComprobanteRepositorio,
)


class ClinicaService:
    # Servicio de aplicación para la gestión clínica: Clientes, Mascotas, Turnos, Consultas y Facturación.

    def __init__(
        self,
        cliente_repo: IClienteRepositorio,
        mascota_repo: IMascotaRepositorio,
        turno_repo: ITurnoRepositorio,
        consulta_repo: IConsultaMedicaRepositorio,
        comprobante_repo: IComprobanteRepositorio,
    ) -> None:
        self._cliente_repo = cliente_repo
        self._mascota_repo = mascota_repo
        self._turno_repo = turno_repo
        self._consulta_repo = consulta_repo
        self._comprobante_repo = comprobante_repo

    # --- CLIENTES ---
    def registrar_cliente(self, nombre: str, apellido: str, dni: str, telefono: str = "", email: str = "") -> Cliente:
        cliente = Cliente(nombre=nombre, apellido=apellido, dni=dni, telefono=telefono, email=email)
        return self._cliente_repo.guardar(cliente)

    def listar_clientes(self) -> List[Cliente]:
        return self._cliente_repo.listar_todos()

    def obtener_cliente(self, id_cliente: int) -> Optional[Cliente]:
        return self._cliente_repo.obtener_por_id(id_cliente)

    # --- MASCOTAS ---
    def registrar_mascota(
        self,
        id_cliente: int,
        nombre: str,
        especie: str = "Canino",
        raza: str = "Mestizo",
        edad: int = 1,
        peso: float = 0.0,) -> Mascota:
        
        cliente = self._cliente_repo.obtener_por_id(id_cliente)
        if cliente is None:
            raise ValueError(f"No existe un cliente registrado con ID {id_cliente}.")
        mascota = Mascota(
            id_cliente=id_cliente,
            nombre=nombre,
            especie=especie,
            raza=raza,
            edad=edad,
            peso=peso,
        )
        return self._mascota_repo.guardar(mascota)

    def listar_mascotas(self) -> List[Mascota]:
        return self._mascota_repo.listar_todos()

    def obtener_mascota(self, id_mascota: int) -> Optional[Mascota]:
        return self._mascota_repo.obtener_por_id(id_mascota)

    # --- TURNOS ---
    def agendar_turno(self, id_mascota: int, veterinario: str, fecha_hora: datetime) -> Turno:
        mascota = self._mascota_repo.obtener_por_id(id_mascota)
        if mascota is None:
            raise ValueError(f"No existe una mascota registrada con ID {id_mascota}.")

        nuevo_turno = Turno(id_mascota=id_mascota, veterinario=veterinario, fecha_hora=fecha_hora)
        turnos_vet = self._turno_repo.listar_por_veterinario(veterinario)
        nuevo_turno.validar_disponibilidad(turnos_vet)
        return self._turno_repo.guardar(nuevo_turno)

    def listar_turnos(self) -> List[Turno]:
        return self._turno_repo.listar_todos()

    def cancelar_turno(self, id_turno: int) -> Turno:
        turno = self._turno_repo.obtener_por_id(id_turno)
        if turno is None:
            raise ValueError(f"No se encontró el turno ID {id_turno}.")
        turno.cancelar()
        self._turno_repo.actualizar(turno)
        return turno

    # --- CONSULTAS Y FACTURACIÓN ---
    def obtener_esquema_vacunas_mascota(self, id_mascota: int) -> Tuple[bool, List[str], List[str]]:
        
        # Evalúa todas las vacunas aplicadas a una mascota con respecto al esquema obligatorio.
        # Retorna (vacunas_al_dia, vacunas_aplicadas_historicas, vacunas_pendientes).
        
        mascota = self._mascota_repo.obtener_por_id(id_mascota)
        if mascota is None:
            raise ValueError(f"No existe una mascota con ID {id_mascota}.")

        # busca la especie de la mascota, si no hay, busca por defecto los generales
        obligatorias = VACUNAS_OBLIGATORIAS.get(mascota.especie, VACUNAS_OBLIGATORIAS["General"])
        consultas = self._consulta_repo.listar_por_mascota(id_mascota)

        aplicadas_historicas: List[str] = []
        aplicadas_lower = set()
        for c in consultas:
            for v in c.vacunas_aplicadas:
                if v.lower() not in aplicadas_lower:
                    aplicadas_lower.add(v.lower())
                    aplicadas_historicas.append(v)

        pendientes = [v for v in obligatorias if v.lower() not in aplicadas_lower]
        al_dia = len(pendientes) == 0
        return al_dia, aplicadas_historicas, pendientes

    def registrar_consulta_y_comprobante(
        self,
        id_mascota: int,
        motivo: str,
        diagnostico: str,
        tratamiento: str,
        veterinario: str,
        vacunas_aplicadas: Optional[List[str]] = None,
        monto_base: float = 0.0,
        tipo_tarifa: str = "Normal",
        id_turno: Optional[int] = None,
        fecha_hora: Optional[datetime] = None,) -> Dict[str, Any]:
        
        mascota = self._mascota_repo.obtener_por_id(id_mascota)
        if mascota is None:
            raise ValueError(f"No existe una mascota registrada con ID {id_mascota}.")

        if id_turno is not None:
            turno = self._turno_repo.obtener_por_id(id_turno)
            if turno is not None and turno.estado == "Pendiente":
                turno.marcar_atendido()
                self._turno_repo.actualizar(turno)

        consulta = ConsultaMedica(
            id_mascota=id_mascota,
            motivo=motivo,
            diagnostico=diagnostico,
            tratamiento=tratamiento,
            veterinario=veterinario,
            vacunas_aplicadas=vacunas_aplicadas or [],
            fecha_hora=fecha_hora or datetime.now(),
        )
        consulta_guardada = self._consulta_repo.guardar(consulta)

        # Control del esquema de vacunas obligatorias tras registrar la consulta
        al_dia, aplicadas, pendientes = self.obtener_esquema_vacunas_mascota(id_mascota)

        # Facturación aplicando Patrón Strategy
        estrategia = obtener_estrategia(tipo_tarifa)
        comprobante = ComprobanteAtencion(
            id_consulta=consulta_guardada.id,
            monto_base=monto_base,
            estrategia=estrategia,
            fecha=consulta_guardada.fecha_hora,
        )
        comprobante_guardado = self._comprobante_repo.guardar(comprobante)

        return {
            "consulta": consulta_guardada,
            "comprobante": comprobante_guardado,
            "vacunas_al_dia": al_dia,
            "vacunas_aplicadas": aplicadas,
            "vacunas_pendientes": pendientes,
        }

    def listar_consultas(self) -> List[ConsultaMedica]:
        return self._consulta_repo.listar_todos()

    def listar_comprobantes(self) -> List[ComprobanteAtencion]:
        return self._comprobante_repo.listar_todos()
