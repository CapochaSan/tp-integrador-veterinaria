from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Union
from datetime import datetime, timedelta

from config import DB_PATH


class DBManager:
    """Administrador de conexión, creación de tablas y carga inicial (Seed) en SQLite3."""

    def __init__(self, db_path: Union[str, Path] = DB_PATH) -> None:
        self._db_path = str(db_path)

    @property
    def db_path(self) -> str:
        return self._db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def inicializar_base_datos(self, cargar_seed: bool = True) -> None:
        """Crea las 8 tablas obligatorias y carga datos de ejemplo si está vacía."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    dni TEXT NOT NULL UNIQUE,
                    telefono TEXT,
                    email TEXT
                );
            """)

            # 2. Mascotas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mascotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    especie TEXT NOT NULL,
                    raza TEXT,
                    edad INTEGER DEFAULT 0,
                    peso REAL DEFAULT 0.0,
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
                );
            """)

            # 3. Turnos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turnos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_mascota INTEGER NOT NULL,
                    veterinario TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    FOREIGN KEY (id_mascota) REFERENCES mascotas(id) ON DELETE CASCADE
                );
            """)

            # 4. Consultas Médicas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultas_medicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_mascota INTEGER NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    diagnostico TEXT,
                    tratamiento TEXT,
                    vacunas_aplicadas TEXT,
                    veterinario TEXT NOT NULL,
                    FOREIGN KEY (id_mascota) REFERENCES mascotas(id) ON DELETE CASCADE
                );
            """)

            # 5. Comprobantes de Atención
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comprobantes_atencion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_consulta INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    monto_base REAL NOT NULL,
                    tipo_tarifa TEXT NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (id_consulta) REFERENCES consultas_medicas(id) ON DELETE CASCADE
                );
            """)

            # 6. Órdenes de Derivación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ordenes_derivacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_consulta INTEGER NOT NULL,
                    id_mascota INTEGER NOT NULL,
                    tipo_estudio TEXT NOT NULL,
                    diagnostico_presuntivo TEXT,
                    fecha_emision TEXT NOT NULL,
                    FOREIGN KEY (id_consulta) REFERENCES consultas_medicas(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_mascota) REFERENCES mascotas(id) ON DELETE CASCADE
                );
            """)

            # 7. Remitos Biológicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS remitos_biologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_remito TEXT NOT NULL UNIQUE,
                    codigo_conservadora TEXT NOT NULL,
                    temperatura_transporte REAL NOT NULL,
                    fecha_envio TEXT,
                    fecha_recepcion TEXT,
                    responsable_envio TEXT,
                    responsable_recepcion TEXT,
                    estado TEXT NOT NULL
                );
            """)

            # 8. Muestras Biológicas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS muestras_biologicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_orden INTEGER NOT NULL,
                    id_remito INTEGER,
                    tipo_muestra TEXT NOT NULL,
                    codigo_precinto TEXT NOT NULL,
                    precinto_roto INTEGER NOT NULL DEFAULT 0,
                    estado TEXT NOT NULL,
                    historial_trazabilidad TEXT NOT NULL,
                    fecha_extraccion TEXT NOT NULL,
                    fecha_recepcion TEXT,
                    fecha_analisis TEXT,
                    resultado TEXT,
                    motivo_rechazo TEXT,
                    FOREIGN KEY (id_orden) REFERENCES ordenes_derivacion(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_remito) REFERENCES remitos_biologicos(id) ON DELETE SET NULL
                );
            """)
            conn.commit()

        if cargar_seed:
            self._cargar_datos_semilla()

    def _cargar_datos_semilla(self) -> None:
        """Carga datos iniciales realistas si la tabla clientes está vacía."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes;")
            if cursor.fetchone()[0] > 0:
                return

            ahora = datetime.now().replace(microsecond=0)

            # 1. Clientes
            clientes_seed = [
                ("Lucía", "Fernández", "34567890", "351-5551234", "lucia.fernandez@mail.com"),
                ("Martín", "Gómez", "31234567", "351-5559876", "martin.gomez@mail.com"),
                ("Carla", "Pérez", "38901234", "351-5554567", "carla.perez@mail.com"),
            ]
            cursor.executemany(
                "INSERT INTO clientes (nombre, apellido, dni, telefono, email) VALUES (?, ?, ?, ?, ?);",
                clientes_seed,
            )

            # 2. Mascotas
            mascotas_seed = [
                (1, "Toby", "Canino", "Golden Retriever", 4, 28.5),
                (1, "Mishi", "Felino", "Siamés", 2, 4.2),
                (2, "Rocco", "Canino", "Bulldog Francés", 5, 13.0),
                (3, "Luna", "Felino", "Común Europeo", 3, 3.8),
            ]
            cursor.executemany(
                "INSERT INTO mascotas (id_cliente, nombre, especie, raza, edad, peso) VALUES (?, ?, ?, ?, ?, ?);",
                mascotas_seed,
            )

            # 3. Turnos
            manana = (ahora + timedelta(days=1)).replace(hour=10, minute=0, second=0)
            turnos_seed = [
                (1, "Dra. Ana López", (ahora - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "Atendido"),
                (2, "Dr. Carlos Ruiz", (ahora - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "Atendido"),
                (3, "Dra. Ana López", manana.strftime("%Y-%m-%d %H:%M:%S"), "Pendiente"),
                (4, "Dr. Carlos Ruiz", (manana + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "Pendiente"),
            ]
            cursor.executemany(
                "INSERT INTO turnos (id_mascota, veterinario, fecha_hora, estado) VALUES (?, ?, ?, ?);",
                turnos_seed,
            )

            # 4. Consultas Médicas (separadas para reflejar historial clínico y vacunas)
            c1_fecha = (ahora - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S")
            c2_fecha = (ahora - timedelta(days=1, hours=6)).strftime("%Y-%m-%d %H:%M:%S")
            c3_fecha = (ahora - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            c4_fecha = (ahora - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

            consultas_seed = [
                (1, c1_fecha, "Control anual y decaimiento", "Anemia leve", "Suplemento vitamínico + Hierro 14 días", "Rabia,Quíntuple", "Dra. Ana López"),
                (2, c2_fecha, "Fiebre y pérdida de apetito", "Posible infección urinaria", "Antibiótico Amoxicilina 7 días", "Rabia", "Dr. Carlos Ruiz"),
                (3, c3_fecha, "Vómitos agudos (Guardia)", "Gastroenteritis aguda", "Antiemético inyectable + Dieta blanda", "Rabia,Quíntuple,Parvovirus", "Dra. Ana López"),
                (4, c4_fecha, "Chequeo dermatológico", "Dermatitis alérgica", "Corticoides tópicos 5 días", "Triple Felina", "Dr. Carlos Ruiz"),
            ]
            cursor.executemany(
                """
                INSERT INTO consultas_medicas
                (id_mascota, fecha_hora, motivo, diagnostico, tratamiento, vacunas_aplicadas, veterinario)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                consultas_seed,
            )

            # 5. Comprobantes de Atención
            comprobantes_seed = [
                (1, c1_fecha, 12000.0, "Normal", 12000.0),
                (2, c2_fecha, 14000.0, "Normal", 14000.0),
                (3, c3_fecha, 15000.0, "Urgencia", 22500.0),
                (4, c4_fecha, 10000.0, "Normal", 10000.0),
            ]
            cursor.executemany(
                "INSERT INTO comprobantes_atencion (id_consulta, fecha, monto_base, tipo_tarifa, total) VALUES (?, ?, ?, ?, ?);",
                comprobantes_seed,
            )

            # 6. Órdenes de Derivación
            ordenes_seed = [
                (1, 1, "Hemograma Completo", "Sospecha de anemia", c1_fecha),
                (2, 2, "Urianálisis y Cultivo", "Infección del tracto urinario", c2_fecha),
                (3, 3, "Perfil Bioquímico Renal/Hepático", "Deshidratación por gastroenteritis", c3_fecha),
                (4, 4, "Raspaje Cutáneo / Micológico", "Dermatofitosis presuntiva", c4_fecha),
            ]
            cursor.executemany(
                "INSERT INTO ordenes_derivacion (id_consulta, id_mascota, tipo_estudio, diagnostico_presuntivo, fecha_emision) VALUES (?, ?, ?, ?, ?);",
                ordenes_seed,
            )

            # 7. Remitos Biológicos
            rem1_envio = (ahora - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
            rem1_rec = (ahora - timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            rem2_envio = (ahora - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")

            remitos_seed = [
                ("REM-2026-001", "CONS-A1", 3.8, rem1_envio, rem1_rec, "Dra. Ana López", "Bioq. Sofía Méndez", "Entregado"),
                ("REM-2026-002", "CONS-B2", 4.2, rem2_envio, None, "Dr. Carlos Ruiz", None, "En Tránsito"),
            ]
            cursor.executemany(
                """
                INSERT INTO remitos_biologicos
                (codigo_remito, codigo_conservadora, temperatura_transporte, fecha_envio, fecha_recepcion, responsable_envio, responsable_recepcion, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                remitos_seed,
            )

            # 8. Muestras Biológicas en distintos estados
            # Muestra 1: Analizada (con tiempos claros de tránsito y análisis para Reporte 4)
            m1_ext = ahora - timedelta(days=2, hours=5)
            m1_rec = ahora - timedelta(days=2, hours=2)
            m1_ana = ahora - timedelta(days=2, hours=0, minutes=30)
            m1_log = "\n".join([
                f"[{m1_ext.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Extraída: Muestra extraída (Precinto: PREC-1001, Tipo: Sangre EDTA).",
                f"[{(m1_ext + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Empaquetada: Muestra acondicionada y empaquetada en conservadora.",
                f"[{rem1_envio}] Estado -> En Tránsito: Conservadora despachada en remito hacia el laboratorio.",
                f"[{m1_rec.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Recibida: Muestra recibida correctamente con precinto intacto.",
                f"[{m1_ana.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Analizada: Análisis finalizado con éxito. Resultado: Hematocrito 34% (Leve disminución), Glóbulos Blancos normales.",
            ])

            # Muestra 2: Rechazada por precinto roto (para Reporte 2)
            m2_ext = ahora - timedelta(days=1, hours=6)
            m2_rec = ahora - timedelta(days=1, hours=3)
            m2_motivo = "Rechazo automático en recepción: Precinto de seguridad violado/roto durante el transporte."
            m2_log = "\n".join([
                f"[{m2_ext.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Extraída: Muestra extraída (Precinto: PREC-1002, Tipo: Orina estéril).",
                f"[{(m2_ext + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Empaquetada: Muestra acondicionada y empaquetada en conservadora.",
                f"[{rem1_envio}] Estado -> En Tránsito: Conservadora despachada en remito hacia el laboratorio.",
                f"[{m2_rec.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Rechazada: {m2_motivo}",
            ])

            # Muestra 3: En Tránsito (lista para recibir desde la UI con o sin precinto roto)
            m3_ext = ahora - timedelta(hours=7)
            m3_log = "\n".join([
                f"[{m3_ext.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Extraída: Muestra extraída (Precinto: PREC-1003, Tipo: Suero sanguíneo).",
                f"[{(m3_ext + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Empaquetada: Muestra acondicionada y empaquetada en conservadora.",
                f"[{rem2_envio}] Estado -> En Tránsito: Conservadora despachada en remito hacia el laboratorio.",
            ])

            # Muestra 4: Extraída (recién tomada, lista para empaquetar desde la UI)
            m4_ext = ahora - timedelta(hours=2)
            m4_log = "\n".join([
                f"[{m4_ext.strftime('%Y-%m-%d %H:%M:%S')}] Estado -> Extraída: Muestra extraída (Precinto: PREC-1004, Tipo: Raspado dérmico).",
            ])

            muestras_seed = [
                (
                    1, 1, "Sangre EDTA", "PREC-1001", 0, "Analizada", m1_log,
                    m1_ext.strftime("%Y-%m-%d %H:%M:%S"),
                    m1_rec.strftime("%Y-%m-%d %H:%M:%S"),
                    m1_ana.strftime("%Y-%m-%d %H:%M:%S"),
                    "Hematocrito 34% (Leve disminución), Glóbulos Blancos normales.",
                    None,
                ),
                (
                    2, 1, "Orina estéril", "PREC-1002", 1, "Rechazada", m2_log,
                    m2_ext.strftime("%Y-%m-%d %H:%M:%S"),
                    m2_rec.strftime("%Y-%m-%d %H:%M:%S"),
                    None,
                    None,
                    m2_motivo,
                ),
                (
                    3, 2, "Suero sanguíneo", "PREC-1003", 0, "En Tránsito", m3_log,
                    m3_ext.strftime("%Y-%m-%d %H:%M:%S"),
                    None,
                    None,
                    None,
                    None,
                ),
                (
                    4, None, "Raspado dérmico", "PREC-1004", 0, "Extraída", m4_log,
                    m4_ext.strftime("%Y-%m-%d %H:%M:%S"),
                    None,
                    None,
                    None,
                    None,
                ),
            ]
            cursor.executemany(
                """
                INSERT INTO muestras_biologicas
                (id_orden, id_remito, tipo_muestra, codigo_precinto, precinto_roto, estado,
                 historial_trazabilidad, fecha_extraccion, fecha_recepcion, fecha_analisis, resultado, motivo_rechazo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                muestras_seed,
            )
            conn.commit()
