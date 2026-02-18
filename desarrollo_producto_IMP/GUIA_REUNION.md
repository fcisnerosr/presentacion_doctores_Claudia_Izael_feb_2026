# Guía de Reunión - Etapas 1 y 2
**Duración**: 25-30 minutos  
**Branch**: `etapa_2_parsing`

---

## 🗂️ Resumen de Archivos Ejecutables

### ETAPA 1: Limpieza y Normalización ✅

| # | Archivo | Comando | Por qué | Qué hace |
|---|---------|---------|---------|----------|
| 1 | `tests/test_data_cleaner.py` | `pytest tests/test_data_cleaner.py -v` | Validar implementación | Ejecuta 31 tests de las 3 funciones. Resultado: 31 passed |
| 2 | `src/data_cleaner.py` | *(solo mostrar código)* | Ver implementación | 3 funciones: `normalize_fortran_scientific()`, `detect_file_encoding()`, `is_valid_data_line()` |
| 3 | `scripts/generar_output_etapa1.py` | `python scripts/generar_output_etapa1.py` | Generar archivo procesado | Convierte 263,417 valores y guarda en `output_provisional/ftglstE1_etapa1.txt` |
| 4 | `notebooks/demo_etapa1.ipynb` | `jupyter notebook notebooks/demo_etapa1.ipynb` | Demostración interactiva | Visualiza 800+ valores con gráficos |

### ETAPA 2: Parsing y Extracción ✅

| # | Archivo | Comando | Por qué | Qué hace |
|---|---------|---------|---------|----------|
| 5 | `tests/test_ftg_parser.py` | `pytest tests/test_ftg_parser.py -v` | Validar parser | 17 tests (16 passing): modelos + parser + integración |
| 6 | `src/models.py` | *(solo mostrar código)* | Ver clases de datos | `FatigueElement` y `ParseResult` |
| 7 | `src/ftg_parser.py` | *(solo mostrar código)* | Ver máquina de estados | Parser con 4 estados |
| 8 | `scripts/generar_output_etapa2.py` | `python scripts/generar_output_etapa2.py` | **⭐ EJECUTAR PRIMERO** | Extrae 350 elementos → CSV |
| 9 | `output_provisional/ftglstE1_etapa2.csv` | Abrir en Excel | **Ver resultados finales** | 350 elementos ordenados por daño |

---

## 🚀 Setup Inicial

```bash
# ⚠️ IMPORTANTE: Activar el entorno PRIMERO (si no, pytest no funcionará)
conda activate procesador_fatiga_sacs

# Verificar que estás en el entorno correcto (debe mostrar procesador_fatiga_sacs al inicio)
# Ejemplo: (procesador_fatiga_sacs) usuario@laptop:~$

# Ir al directorio
cd /home/fcisnerosr/github/desarrollo_producto_IMP

# Verificar branch
git branch  # Debe mostrar: * etapa_2_parsing

# Ejecutar todos los tests
pytest tests/ -v
```

**Nota**: Si ves el error `Command 'pytest' not found`, significa que **no activaste el entorno**. Ejecuta `conda activate procesador_fatiga_sacs` primero.

---

## 📊 Orden de Demostración (Recomendado)

### 1️⃣ Mostrar Métricas Generales (2 min)
```bash
# ⚠️ Asegúrate de estar en el entorno: conda activate procesador_fatiga_sacs
pytest tests/ -v --tb=no | tail -5
```
**Resultado esperado**: `47 passed in 1.78s`

### 2️⃣ Generar Output Etapa 2 (2 min)
```bash
python scripts/generar_output_etapa2.py
```
**Resultado esperado**:
```
GENERACIÓN DE OUTPUT PROVISIONAL - ETAPA 2
Elementos extraídos: 350
Daño máximo: 1.234410
Elemento crítico: 404L_0426 J491_24B (RIGHT) ⚠️
```

### 3️⃣ Abrir CSV en Excel (5 min)
```bash
# Abrir desde explorador o con LibreOffice
xdg-open output_provisional/ftglstE1_etapa2.csv
```
**Puntos a destacar**:
- 350 filas × 14 columnas
- Ordenado por MAX_DAMAGE (descendente)
- **Elemento crítico con daño > 1.0** requiere atención inmediata

### 4️⃣ Revisar Código del Parser (5 min)
Abrir `src/ftg_parser.py` y explicar:
- **Máquina de estados** (4 estados con transiciones claras)
- **Método `parse_file()`** (lógica principal de parsing)
- **Transiciones de estado**: SEARCHING → HEADER → ELEMENT → TOTAL

### 5️⃣ Mostrar Tests de Integración (3 min)
```bash
pytest tests/test_ftg_parser.py::TestIntegrationParser -v
```
**Resultado esperado**: 2 tests passing (parseo de archivo real de 146K líneas)

### 6️⃣ Revisar Documentación (5 min)
Abrir `docs/RESUMEN_ETAPA_2.md` y destacar:
- ✅ 350 elementos extraídos (meta era ≥100)
- ✅ 94% de tests passing
- ⚠️ Elemento crítico 404L_0426 con daño 1.234410
- 📊 Distribución de daños (78% bajo riesgo, 1% crítico)

### 7️⃣ Discutir Próximos Pasos (3 min)
- **Etapa 3**: Consolidación (sumar daños de múltiples archivos)
- **Riesgo**: ¿Qué hacer si archivos tienen elementos diferentes?
- **Timeline**: 2-3 días desarrollo + 1 día testing

---

## 📋 Checklist de Reunión

### Antes:
- [ ] **⚠️ CRÍTICO**: Activar entorno: `conda activate procesador_fatiga_sacs`
- [ ] Verificar que el prompt muestra `(procesador_fatiga_sacs)` al inicio
- [ ] Verificar branch: `git checkout etapa_2_parsing`
- [ ] Ejecutar tests: `pytest tests/ -v` (verificar 47 passing)
- [ ] Generar CSV: `python scripts/generar_output_etapa2.py`
- [ ] Abrir archivos en VS Code:
  - [ ] `src/ftg_parser.py`
  - [ ] `output_provisional/ftglstE1_etapa2.csv` (en Excel/LibreOffice)
  - [ ] `docs/RESUMEN_ETAPA_2.md`

### Durante:
- [ ] Demostrar generación de CSV
- [ ] Mostrar elemento crítico en CSV (primera fila)
- [ ] Explicar máquina de estados del parser
- [ ] Mostrar tests de integración pasando
- [ ] Discutir hallazgo: formato SACS tiene columnas CHD/BRC no documentadas

### Después:
- [ ] Documentar feedback del superior
- [ ] Si aprobado → crear branch `etapa_3_consolidacion`
- [ ] Si cambios → implementar y re-testear

---

## ⚠️ Puntos Críticos a Discutir

### 1. Elemento con Daño > 1.0
```
JOINT:     404L_0426
MEMBER:    J491_24B
GRUP:      1_P
DAÑO:      1.234410 (ubicación RIGHT)
ESTADO:    ⚠️ FALLA ESPERADA (daño > 1.0)
```
**Pregunta**: ¿Requiere revisión estructural antes de continuar con Etapa 3?

### 2. Formato SACS No Documentado
Descubrimos columnas adicionales (`CHD`, `BRC`) no especificadas en documentación.  
**Pregunta**: ¿Es formato estándar de SACS o específico de este proyecto IMP?

### 3. Advertencias en Parsing
1,289 advertencias por líneas con guiones o formato irregular (no son errores).  
**Pregunta**: ¿Son esperadas estas líneas o indican problema en datos fuente?

---

## 📁 Archivos de Referencia Rápida

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Estado del proyecto y estructura |
| `docs/implementacion_etapa_1.md` | Documentación técnica Etapa 1 |
| `docs/implementacion_etapa_2.md` | Documentación técnica Etapa 2 (completa con diagramas) |
| `docs/RESUMEN_ETAPA_2.md` | **Resumen ejecutivo** para revisión rápida |
| `output_provisional/ftglstE1_etapa2.csv` | **Output principal** de Etapa 2 |

---

## 🎯 Objetivos de la Reunión

1. ✅ **Validar** que Etapa 2 cumple objetivos técnicos
2. ✅ **Aprobar** diseño de máquina de estados del parser
3. ⚠️ **Discutir** elemento crítico 404L_0426 (daño > 1.0)
4. 🚀 **Obtener aprobación** para iniciar Etapa 3 (Consolidación)
5. 📋 **Resolver dudas** sobre formato SACS y advertencias

---

## 🔍 Preguntas para el Superior

1. ¿El elemento 404L_0426 con daño 1.234410 es esperado? ¿Requiere acción inmediata?
2. ¿Las columnas CHD y BRC son estándar en SACS o específicas del proyecto?
3. ¿Aprobar el enfoque de máquina de estados para Etapa 3 (consolidación)?
4. ¿Continuar con suma aritmética simple o aplicar algún factor de corrección?
5. ¿Timeline de 2-3 días para Etapa 3 es aceptable?
