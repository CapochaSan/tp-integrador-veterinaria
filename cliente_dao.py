from database import conectar
from cliente import Cliente

COLUMNAS = "tipo_dni, nro_dni, nombre, apellido, estado"


class ClienteDAO:
    def __init__(self):
        self.crear_tabla()

    def crear_tabla(self):
        conexion = conectar()
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                tipo_dni TEXT NOT NULL,
                nro_dni INT NOT NULL,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Activo',
                PRIMARY KEY (tipo_dni, nro_dni))
                """)
        conexion.commit()
        conexion.close()

    # Convierte una fila de la base en un objeto Cliente
    # (el orden de las posiciones es el de COLUMNAS)
    def fila_a_cliente(self, fila):
        if fila is None:
            return None
        return Cliente(fila[0], fila[1], fila[2], fila[3], fila[4])

    # ------------------------------------------------------------------------------- ALTA ------------------------------------------------------------------------------
    def agregar(self, cliente):
        conexion = conectar()
        conexion.execute(
            "INSERT INTO cliente (tipo_dni, nro_dni, nombre, apellido, estado) VALUES (?, ?, ?, ?, ?)",
            (cliente.tipo_dni, cliente.nro_dni, cliente.nombre, cliente.apellido, cliente.estado))
        conexion.commit()
        conexion.close()
        return cliente

    # ----------------------------------------------------------------------------- CONSULTAS --------------------------------------------------------------------------

    def buscar_por_documento(self, tipo_dni, nro_dni):
        conexion = conectar()
        fila = conexion.execute(
            f"SELECT {COLUMNAS} FROM cliente WHERE tipo_dni = ? AND nro_dni = ?",
            (tipo_dni, nro_dni)).fetchone()
        conexion.close()
        return self.fila_a_cliente(fila)

    def listar(self, incluir_inactivos=False):
        sql = f"SELECT {COLUMNAS} FROM cliente"
        if not incluir_inactivos:
            sql += " WHERE estado = 'Activo'"
        sql += " ORDER BY apellido, nombre"
        conexion = conectar()
        filas = conexion.execute(sql).fetchall()
        conexion.close()
        return [self.fila_a_cliente(f) for f in filas]

    # ---- MODIFICACIÓN (sirve también para la baja lógica) ----
    # El documento no se cambia: identifica al cliente (va en el WHERE)
    def modificar(self, cliente):
        conexion = conectar()
        conexion.execute(
            "UPDATE cliente SET nombre = ?, apellido = ?, estado = ? "
            "WHERE tipo_dni = ? AND nro_dni = ?",
            (cliente.nombre, cliente.apellido, cliente.estado, cliente.tipo_dni, cliente.nro_dni))
        conexion.commit()
        conexion.close()