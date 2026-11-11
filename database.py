import os
import sqlite3
 
# La base se guarda al lado de este archivo, sin importar desde dónde se ejecute
ARCHIVO_BD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veterinaria.db")
 
 
def conectar():
    conexion = sqlite3.connect(ARCHIVO_BD)
    conexion.execute("PRAGMA foreign_keys = ON")   # activa las claves foráneas
    return conexion
 