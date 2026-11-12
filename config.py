from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Ruta de la Base de Datos SQLite
DB_PATH = BASE_DIR / "tp_veterinaria.db"

# Directorio donde se guardan los reportes PDF generados
REPORTES_DIR = BASE_DIR / "reportes_generados"
REPORTES_DIR.mkdir(parents=True, exist_ok=True)

# Esquema de vacunas obligatorias por especie
VACUNAS_OBLIGATORIAS = {
    "Canino": ["Rabia", "Quíntuple", "Parvovirus"],
    "Felino": ["Rabia", "Triple Felina", "Leucemia Felina"],
    "General": ["Rabia", "Desparasitación Anual"]
}
