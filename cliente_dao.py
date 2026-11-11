from database import conectar
from cliente import Cliente
 
 
class ClienteDAO:
    def __init__(self):
        self.crear_tabla()
 
    def crear_tabla(self):
        conexion = conectar()
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_dni TEXT NOT NULL,
                nro_dni INT NOT NULL,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'activo',
                UNIQUE (tipo_dni, nro_dni)
            )
        """)
        conexion.commit()
        conexion.close()
 
    # Convierte una fila de la base en un objeto Cliente
    def fila_a_cliente(self, fila):
        if fila is None:
            return None
        return Cliente(fila[1], fila[2], fila[3], fila[4], fila[0])
 
    # ------------------------------------------------------------------------------- ALTA ------------------------------------------------------------------------------
    def agregar(self, cliente):
        conexion = conectar()
        cursor = conexion.execute(
            "INSERT INTO cliente (tipo_dni, nro_dni, nombre, apellido, estado) VALUES (?, ?, ?, ?, ?)",
            (cliente.tipo_dni, cliente.nro_dni, cliente.nombre, cliente.apellido, cliente.estado))
        conexion.commit()
        cliente.id_cliente = cursor.lastrowid
        conexion.close()
        return cliente
 
    # ----------------------------------------------------------------------------- CONSULTAS --------------------------------------------------------------------------
 
    def buscar_por_documento(self, tipo_dni, nro_dni):
        conexion = conectar()
        fila = conexion.execute("SELECT * FROM cliente WHERE tipo_dni = ? AND nro_dni = ?",
                                (tipo_dni, nro_dni)).fetchone()
        conexion.close()
        return self.fila_a_cliente(fila)
 
    def listar(self, incluir_inactivos=False):
        sql = "SELECT * FROM cliente"
        if not incluir_inactivos:
            sql += " WHERE estado = 'Activo'"
        sql += " ORDER BY apellido, nombre"
        conexion = conectar()
        filas = conexion.execute(sql).fetchall()
        conexion.close()
        return [self.fila_a_cliente(f) for f in filas]
 
    # ---- MODIFICACIÓN (sirve también para la baja lógica) ----
    def modificar(self, cliente):
        conexion = conectar()
        conexion.execute(
            "UPDATE cliente SET tipo_dni = ?, nro_dni = ?, nombre = ?, apellido = ?, estado = ? "
            "WHERE nro_dni = ?",
            (cliente.tipo_dni, cliente.nro_dni, cliente.nombre, cliente.apellido, cliente.estado, cliente.nro_dni))
        conexion.commit()
        conexion.close()