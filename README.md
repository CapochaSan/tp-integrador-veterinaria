# Red de Clínicas Veterinarias & Derivación de Laboratorio 🐾🧪

Sistema de gestión integral para atención clínica veterinaria, control de turnos, facturación dinámica y trazabilidad inmutable en la derivación de muestras biológicas hacia el laboratorio central. Desarrollado para la asignatura **Desarrollo de Aplicaciones con Objetos (DAO) — UTN FRC (2026)**.

---

## 👥 Integrantes — Grupo 10

- **Santiago Vagni** — Legajo: `90149`
- **María Eugenia Moreno Venturini** — Legajo: `84149`

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.x
- **Interfaz Gráfica (GUI):** Flet
- **Base de Datos:** SQLite3 (con integridad referencial activa y *seeding* inicial)
- **Generación de Reportes:** ReportLab (PDF)
- **Testing Unitario e Integración:** PyTest
- **Control de Versiones:** Git & GitHub

---

## ⚙️ Arquitectura del Proyecto

El sistema implementa una **Arquitectura en Capas** aplicando **Inversión de Dependencias (DIP)**: la capa de dominio define contratos abstractos (`ABC`) y contiene todas las reglas de negocio, permaneciendo completamente desacoplada de SQLite, ReportLab y Flet.

```text
tp_integrador_veterinaria/
├── main.py                         # Punto de entrada de la aplicación (Flet)
├── config.py                       # Configuraciones globales (rutas de BD y PDFs)
├── requeriments.txt                # Dependencias del proyecto
├── README.md                       # Documentación técnica del proyecto
├── reportes_generados/             # Salida de comprobantes y reportes analíticos en PDF
│
├── src/
│   ├── domain/                     # CAPA DE DOMINIO Y LÓGICA DE NEGOCIO
│   │   ├── interfaces/             # Contratos abstractos de repositorios (ABC)
│   │   ├── models/                 # 8 Entidades principales del dominio
│   │   ├── patterns/               # Implementación de State, Strategy y Factories
│   │   └── services/               # Casos de uso (ClinicaService, LaboratorioService)
│   │
│   ├── infrastructure/             # CAPA DE INFRAESTRUCTURA Y ADAPTADORES
│   │   ├── database/               # DBManager (conexión SQLite3, DDL y carga semilla)
│   │   ├── repositories/           # Repositorios concretos sobre SQLite3
│   │   └── reports/                # GeneradorPDF con ReportLab
│   │
│   └── ui/                         # CAPA DE PRESENTACIÓN (FLET)
│       ├── components/             # Componentes visuales reutilizables
│       └── views/                  # Vistas del flujo clínico, laboratorio y reportes
│
└── tests/                          # SUITE DE PRUEBAS AUTOMATIZADAS (PyTest)
    ├── conftest.py                 # Fixtures de base de datos en memoria/temporal
    ├── test_turnos.py              # Validación de superposición horaria
    ├── test_facturacion.py         # Pruebas del patrón Strategy y liquidación
    ├── test_muestra_state.py       # Transiciones de estado y rechazo por precinto roto
    └── test_integracion_flujo.py   # Prueba de extremo a extremo (Clínica -> Laboratorio)
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
