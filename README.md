# Red de Clínicas Veterinarias & Derivación de Laboratorio 🐾🧪

Sistema de gestión integral para atención clínica veterinaria y trazabilidad inmutable en la derivación de muestras biológicas al laboratorio central, desarrollado para la asignatura *Desarrollo de Aplicaciones con Objetos* (2026).

---

## 👥 Integrantes - Grupo 10
* **Santiago Vagni** (Legajo: 90149)
* **Gonzalo Munafó** (Legajo: 96940)
* **María Eugenia Moreno Venturini** (Legajo: 84149)

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica (GUI):** [Flet](https://flet.dev/) (Flutter for Python)
* **Base de Datos:** SQLite3
* **Generación de Reportes:** ReportLab (PDF)
* **Testing Unitario:** PyTest
* **Control de Versiones:** Git & GitHub

---

## ⚙️ Arquitectura del Proyecto

El sistema está diseñado bajo una **Arquitectura en Capas** aplicando el principio de **Inversión de Dependencias (DIP)** para desacoplar el dominio de la infraestructura (persistencia y GUI).

```text
tp_integrador_veterinaria/
├── main.py                     # Punto de entrada de la aplicación
├── config.py                   # Configuraciones globales
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Presentación del proyecto
│
├── src/
│   ├── domain/                 # LÓGICA DE NEGOCIO Y DOMINIO
│   │   ├── models/             # Entidades principales (Cliente, Mascota, Muestra, etc.)
│   │   ├── services/           # Casos de uso y reglas de negocio
│   │   └── interfaces/         # Contratos/Abstracciones (Repositories Interfaces)
│   │
│   ├── infrastructure/         # PERSISTENCIA Y ADAPTADORES EXTERNOS
│   │   ├── database/           # Conexión y scripts de SQLite
│   │   ├── repositories/       # Implementación concreta de repositorios
│   │   └── reports/            # Generación de comprobantes y reportes en PDF (ReportLab)
│   │
│   └── ui/                     # CAPA DE PRESENTACIÓN (FLET)
│       ├── components/         # Componentes visuales reutilizables
│       └── views/              # Vistas/Pantallas según proceso de negocio
│
└── tests/                      # PRUEBAS UNITARIAS (PyTest)
    ├── test_muestra_estado.py
    └── test_cliente_mascota.py
```

---

## 📌 Procesos de Negocio & Trazabilidad

1. **Gestión Clínica:** Alta de clientes, mascotas e historial clínico.
2. **Atención Médica y Ordenes:** Registro de consultas y emisión de órdenes de derivación.
3. **Cadena de Custodia & Muestras:** Empaquetado en conservadoras isotérmicas y control de precintos sanitarios (implementando el patrón *State* para el ciclo de vida de la muestra).
4. **Recepción en Laboratorio:** Verificación del precinto sanitario y control automatizado de rechazo si se encuentra roto.
5. **Carga de Resultados y Comprobantes:** Registro de análisis y emisión de comprobantes.
6. **Módulo de Reportes Analíticos:** Tiempos de tránsito, muestras rechazadas, tratamientos aplicados y facturación.

---

## 🎨 Patrones de Diseño Aplicados
* **State Pattern:** Para administrar el ciclo de vida inmutable de la `MuestraBiologica` (*Extraída $\rightarrow$ Empaquetada $\rightarrow$ En tránsito $\rightarrow$ Recibida $\rightarrow$ Analizada / Rechazada*).
* **Factory / Repository Pattern:** Para la abstracción de persistencia y creación de reportes PDF.

---

## 🚀 Instrucciones de Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/tp-integrador.git](https://github.com/tu-usuario/tp-integrador.git)
   cd tp-integrador
   ```

2. **Crear y activar entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Linux/macOS
   .venv\Scripts\activate     # En Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

5. **Ejecutar pruebas unitarias:**
   ```bash
   pytest
   ```