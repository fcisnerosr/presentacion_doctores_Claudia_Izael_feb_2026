# Procesador de Fatiga SACS v1.0

**Instituto Mexicano del Petróleo**  
Copyright © 2026 Instituto Mexicano del Petróleo. Todos los derechos reservados.

---

## 📋 Descripción

Herramienta especializada para ingenieros estructurales que consolida reportes de análisis de fatiga generados por **SACS (Structural Analysis Computer System)**. El software procesa múltiples archivos de texto que representan diferentes etapas temporales de operación, suma aritméticamente el daño acumulado por fatiga, y genera reportes consolidados en formato Excel.

### Problema que Resuelve
SACS **NO suma automáticamente** el daño de fatiga entre diferentes modelos temporales (ej. años 0-10, 10-20, 20-30). Los ingenieros deben hacerlo manualmente, proceso propenso a errores y extremadamente tedioso con miles de elementos estructurales.

---

## 🎯 Estado del Proyecto: Etapa 2 - Parsing y Extracción

**Branch actual**: `etapa_2_parsing`  
**Objetivo**: Implementar parser con máquina de estados para extraer elementos estructurales y valores de daño por fatiga

### Progreso de Etapas
- [x] Etapa 0: Análisis y documentación
- [x] **Etapa 1: Limpieza y Normalización** ✅ COMPLETADA
- [🔄] **Etapa 2: Parsing y Extracción** ← ACTUALMENTE AQUÍ
- [ ] Etapa 3: Consolidación y Suma
- [ ] Etapa 4: Interfaz Gráfica (GUI)
- [ ] Etapa 5: Exportación y Reportes
- [ ] Etapa 6: Testing y Validación
- [ ] Etapa 7: Empaquetado

---

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd desarrollo_producto_IMP
git checkout etapa_2_parsing
```

### 2. Instalar Dependencias
```bash
# Con Mamba (recomendado)
mamba env create -f environment.yml
mamba activate procesador_fatiga_sacs

# O con Conda
conda env create -f environment.yml
conda activate procesador_fatiga_sacs
```

Ver [INSTALL.md](docs/INSTALL.md) para instrucciones detalladas.

### 3. Verificar Instalación
```bash
# Ejecutar tests (47 tests totales)
pytest tests/ -v

# Generar output provisional Etapa 1
python scripts/generar_output_etapa1.py

# Generar output provisional Etapa 2
python scripts/generar_output_etapa2.py
```

---

## 📁 Estructura del Proyecto

```
desarrollo_producto_IMP/
├── data/                       # Archivos de prueba SACS
│   └── ftglstE1.txt
├── docs/                       # Documentación técnica
│   ├── INSTALL.md
│   ├── implementacion_etapa_1.md
│   ├── dificultades_tecnicas/
│   ├── etapas_proyecto/
│   └── plan_desarrollo_producto/
├── src/                        # Código fuente (por etapas)
│   ├── data_cleaner.py         # Etapa 1: Limpieza
│   ├── models.py               # Etapa 2: Modelos de datos
│   └── ftg_parser.py           # Etapa 2: Parser con máquina de estados
├── tests/                      # Tests unitarios e integración
│   ├── test_data_cleaner.py    # 31 tests, 100% passing
│   └── test_ftg_parser.py      # 17 tests, 94% passing
├── notebooks/                  # Demos para revisión
│   └── demo_etapa1.ipynb
├── scripts/                    # Scripts de utilidad
│   ├── generar_output_etapa1.py
│   └── generar_output_etapa2.py
├── output_provisional/         # Outputs de validación por etapa
│   ├── README.md
│   ├── ftglstE1_etapa1.txt     # 263,417 valores convertidos
│   └── ftglstE1_etapa2.csv     # 350 elementos extraídos
├── environment.yml             # Dependencias conda/mamba
├── docs/INSTALL.md             # Instrucciones de instalación
└── README.md                   # Este archivo
```

---

## 📖 Documentación

- **[Implementación Etapa 1](docs/implementacion_etapa_1.md)**: Limpieza y normalización de datos SACS
- **[Implementación Etapa 2](docs/implementacion_etapa_2.md)**: Parser con máquina de estados y extracción estructurada
- **[Dificultades Técnicas](docs/dificultades_tecnicas/dificultades_tecnicas.md)**: Análisis profundo de los 8 desafíos técnicos identificados
- **[Etapas del Proyecto](docs/etapas_proyecto/etapas_del_proyecto.md)**: Roadmap completo de 7 etapas con cronograma
- **[INSTALL.md](docs/INSTALL.md)**: Guía de instalación paso a paso

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src tests/

# Tests específicos de Etapa 1
pytest tests/test_data_cleaner.py -v
```

---

## 🤝 Workflow de Desarrollo (Por Etapas)

1. **Desarrollo en branch**: `etapa_X_nombre`
2. **Validación con superior**: Demo + tests pasando
3. **Merge a main**: Solo cuando la etapa está aprobada
4. **Nueva etapa**: Branch desde main actualizado

### Comandos Git Útiles
```bash
# Ver rama actual
git branch

# Cambiar de etapa
git checkout etapa_2_parsing

# Actualizar desde main
git fetch origin
git merge origin/main
```

---

## 📊 Datos de Prueba

El archivo [data/ftglstE1.txt](data/ftglstE1.txt) contiene:
- **146,370 líneas** de output real de SACS
- Reportes de fatiga de 16 casos de carga
- Notación científica Fortran (formato problemático)
- Múltiples elementos estructurales (joints, members)

---

## 🏗️ Tecnologías

- **Python 3.11**: Lenguaje principal
- **NumPy**: Manejo de arrays numéricos
- **Pandas**: Manipulación de datos tabulares
- **Pytest**: Framework de testing
- **Tkinter**: GUI (Etapa 4)
- **OpenPyXL**: Exportación a Excel (Etapa 5)

---

## 📄 Licencia

Código propietario del Instituto Mexicano del Petróleo.  
**Uso, reproducción o distribución sin autorización expresa está prohibido.**

---

## 👥 Contacto

**Instituto Mexicano del Petróleo**  
Proyecto: Desarrollo de Producto - Procesador de Fatiga SACS
