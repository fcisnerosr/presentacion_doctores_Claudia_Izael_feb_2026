# Instrucciones de Instalación - Procesador de Fatiga SACS v1.0

## Prerequisitos
- **Mamba** o **Conda** instalado
- Git

## Instalación del Entorno

### Opción 1: Con Mamba (Recomendado - Más rápido)
```bash
# Crear entorno desde el archivo environment.yml
mamba env create -f environment.yml

# Activar el entorno
mamba activate procesador_fatiga_sacs

# Verificar instalación
python --version  # Debe mostrar Python 3.11.x
pytest --version  # Debe mostrar pytest 7.4.x
```

### Opción 2: Con Conda
```bash
# Crear entorno
conda env create -f environment.yml

# Activar el entorno
conda activate procesador_fatiga_sacs
```

### Actualizar el entorno (si se añaden nuevas dependencias)
```bash
mamba env update -f environment.yml --prune
```

## Verificación de Instalación

```bash
# Ejecutar tests (cuando estén disponibles)
pytest tests/ -v

# Verificar imports
python -c "import numpy; import pandas; print('✓ Librerías instaladas correctamente')"
```

## Estructura del Proyecto por Etapas

### Etapa 1: Limpieza y Normalización (Actual)
**Branch**: `etapa_1_limpieza_datos`

**Dependencias principales**:
- numpy
- pytest
- jupyter (para demos)

**Entregables**:
- `src/data_cleaner.py`: Funciones de normalización
- `tests/test_data_cleaner.py`: Suite de tests
- `notebooks/demo_etapa1.ipynb`: Demostración interactiva

### Etapas Futuras
- **Etapa 2**: Parsing (añadir re, logging)
- **Etapa 3**: Consolidación (pandas intensivo)
- **Etapa 4**: GUI (tkinter - incluido en Python)
- **Etapa 5**: Exportación (openpyxl, xlsxwriter)
- **Etapa 6**: Testing final
- **Etapa 7**: Empaquetado (pyinstaller)

## Comandos Útiles

```bash
# Listar entornos
mamba env list

# Remover entorno (si necesitas empezar de cero)
mamba env remove -n procesador_fatiga_sacs

# Exportar entorno instalado (para replicar en otra máquina)
mamba env export > environment_lock.yml
```

## Troubleshooting

### Error: "mamba: command not found"
Instalar mamba:
```bash
conda install -c conda-forge mamba
```

### Error: "Solving environment: failed"
Intentar con conda en lugar de mamba, o usar:
```bash
mamba env create -f environment.yml --force
```

### Conflictos de versiones
Editar `environment.yml` y remover restricciones de versión (`>=`), luego:
```bash
mamba env update -f environment.yml --prune
```
