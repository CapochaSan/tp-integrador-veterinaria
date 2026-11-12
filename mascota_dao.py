from database import conectar
from cliente import Cliente
from cliente_dao import ClienteDAO
from mascota import Mascota


# Los datos del cliente se guardan como clave foránea y se reconstruyen como
# objeto Cliente al leer una mascota. De esta manera Mascota mantiene la
# agregación sin duplicar los datos personales del cliente.
COLUMNAS = "m.nombre, m.especie, c.tipo_dni, c.nro_dni, c.nombre, c.apellido, m.estado"

class MascotaDAO:
    def __init__(self):
        # Asegura que la tabla referenciada exista antes de crear la relación.
        ClienteDAO()
        self.crear_tabla()

    def crear_tabla(self):
        conexion = conectar()
        try:
            definicion = """
                CREATE TABLE IF NOT EXISTS mascota (
            nombre TEXT NOT NULL,
            especie TEXT NOT NULL,
            tipo_dni TEXT NOT NULL,
            nro_dni INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Activo',
            PRIMARY KEY (nombre, tipo_dni, nro_dni),
            FOREIGN KEY (tipo_dni, nro_dni)
            REFERENCES cliente (tipo_dni, nro_dni)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
                )
            """
            info = conexion.execute("PRAGMA table_info(mascota)").fetchall()
            if "estado" not in [fila[1] for fila in info]:
                conexion.execute(
                    "ALTER TABLE mascota ADD COLUMN estado TEXT NOT NULL DEFAULT 'Activo'"
                )

            if info:
                clave_primaria = tuple(
                    fila[1]
                    for fila in sorted((fila for fila in info if fila[5]), key=lambda fila: fila[5])
                )
                if clave_primaria != ("nombre", "tipo_dni", "nro_dni"):
                    # La versión anterior usaba al cliente como clave primaria,
                    # lo que impedía registrar más de una mascota por cliente.
                    huérfanas = conexion.execute(
                        "SELECT COUNT(*) FROM mascota AS m "
                        "LEFT JOIN cliente AS c "
                        "ON c.tipo_dni = m.tipo_dni AND c.nro_dni = m.nro_dni "
                        "WHERE c.tipo_dni IS NULL"
                    ).fetchone()[0]
                    if huérfanas:
                        raise ValueError(
                            "No se puede actualizar mascota: hay registros sin un cliente asociado."
                        )
                    conexion.execute("BEGIN")
                    try:
                        conexion.execute(definicion.replace("mascota (", "mascota_nueva (", 1))
                        conexion.execute(
                            "INSERT INTO mascota_nueva (nombre, especie, tipo_dni, nro_dni) "
                            "SELECT nombre, especie, tipo_dni, nro_dni FROM mascota"
                        )
                        conexion.execute("DROP TABLE mascota")
                        conexion.execute("ALTER TABLE mascota_nueva RENAME TO mascota")
                        conexion.commit()
                    except Exception:
                        conexion.rollback()
                        raise
                else:
                    conexion.execute(definicion)
            else:
                conexion.execute(definicion)
            conexion.commit()
        finally:
            conexion.close()

    def fila_a_mascota(self, fila):
        if fila is None:
            return None

        cliente = Cliente(fila[2], fila[3], fila[4], fila[5], "Activo")
        mascota = Mascota(fila[0], fila[1], cliente)
        mascota.estado = fila[6]

        return mascota

    def agregar(self, mascota):
        error = mascota.validar()
        if error:
            raise ValueError(error)
        if not isinstance(mascota.cliente, Cliente):
            raise TypeError("La mascota debe estar asociada a un objeto Cliente.")

        conexion = conectar()
        try:
            conexion.execute(
                "INSERT INTO mascota (nombre, especie, tipo_dni, nro_dni, estado) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    mascota.nombre,
                    mascota.especie,
                    mascota.cliente.tipo_dni,
                    mascota.cliente.nro_dni,
                    mascota.estado
                ),
            )
            conexion.commit()
        finally:
            conexion.close()
        return mascota

    def buscar_por_cliente(self, tipo_dni, nro_dni):
        """Devuelve todas las mascotas asociadas al documento del cliente."""
        conexion = conectar()
        try:
            filas = conexion.execute(
                f"SELECT {COLUMNAS} FROM mascota AS m "
                "JOIN cliente AS c ON c.tipo_dni = m.tipo_dni AND c.nro_dni = m.nro_dni "
                "WHERE m.tipo_dni = ? AND m.nro_dni = ? "
                "ORDER BY m.nombre",
                (tipo_dni, nro_dni),
            ).fetchall()
        finally:
            conexion.close()
        return [self.fila_a_mascota(fila) for fila in filas]

    def buscar_por_nombre(self, nombre, tipo_dni, nro_dni):
        conexion = conectar()
        try:
            fila = conexion.execute(
                f"SELECT {COLUMNAS} FROM mascota AS m "
                "JOIN cliente AS c ON c.tipo_dni = m.tipo_dni "
                "AND c.nro_dni = m.nro_dni "
                "WHERE m.nombre = ? AND m.tipo_dni = ? AND m.nro_dni = ?",
                (nombre, tipo_dni, nro_dni),
            ).fetchone()
        finally:
            conexion.close()

        return self.fila_a_mascota(fila)

    def listar(self, mostrar_inactivos=False):
        conexion = conectar()
        try:
            consulta = (
                f"SELECT {COLUMNAS} FROM mascota AS m "
                "JOIN cliente AS c ON c.tipo_dni = m.tipo_dni "
                "AND c.nro_dni = m.nro_dni "
            )

            if not mostrar_inactivos:
                consulta += "WHERE m.estado = 'Activo' "

            consulta += "ORDER BY m.nombre, c.apellido, c.nombre"

            filas = conexion.execute(consulta).fetchall()
        finally:
            conexion.close()

        return [self.fila_a_mascota(fila) for fila in filas]
    
    def modificar(self, mascota, nombre_original=None):
        error = mascota.validar()
        if error:
            raise ValueError(error)

        nombre_original = nombre_original or mascota.nombre

        conexion = conectar()
        try:
            cursor = conexion.execute(
                """
                UPDATE mascota
                SET nombre = ?, especie = ?, estado = ?
                WHERE nombre = ? AND tipo_dni = ? AND nro_dni = ?
                """,
                (
                    mascota.nombre,
                    mascota.especie,
                    mascota.estado,
                    nombre_original,
                    mascota.cliente.tipo_dni,
                    mascota.cliente.nro_dni,
                ),
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            conexion.close()

    def eliminar(self, nombre, tipo_dni, nro_dni):
        
        conexion = conectar()
        try:
            cursor = conexion.execute(
                "DELETE FROM mascota "
                "WHERE nombre = ? AND tipo_dni = ? AND nro_dni = ?",
                (nombre, tipo_dni, nro_dni),
            )
            try:
                conexion.commit()
            except Exception:
                conexion.rollback()
                raise
        finally:
            conexion.close()
        return cursor.rowcount > 0
    
