# Estrategia de Implementación - Etapa 1

## Limpieza y Normalización de Datos SACS

**Fecha**: 04 de Febrero, 2026  
**Branch**: `etapa_1_limpieza_datos`  
**Objetivo**: Implementar funciones robustas para normalizar datos de SACS

---

## 1. Enfoque de Desarrollo

### Test-Driven Development (TDD) Adaptado

```
┌─────────────────────────────────────────────────────────┐
│  Ciclo de Desarrollo por Etapa                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Escribir función simple (versión "funcional")       │
│     ↓                                                    │
│  2. Crear tests con casos de prueba mínimos             │
│     ↓                                                    │
│  3. Crear notebook demo interactivo                     │
│     ↓                                                    │
│  4. Validar con datos reales (ftglstE1.txt)             │
│     ↓                                                    │
│  5. Reunión con superior → Feedback                     │
│     ↓                                                    │
│  6. Refinar código (agregar manejo de errores)          │
│     ↓                                                    │
│  7. Merge a main (código "pulido")                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Implementación en 3 Niveles

### Nivel 1: Versión "Funcional" (Branch de Etapa)

**Objetivo**: QUE FUNCIONE, no perfección

```python
# En etapa_1_limpieza_datos
# src/data_cleaner.py

def normalize_fortran_scientific(value_str):
    """Convierte .123-4 a 0.123E-04"""
    # Versión directa, sin manejo exhaustivo de errores
    import re
    value_str = re.sub(r'(\.\d+)([+-])(\d+)', r'0\1E\2\3', value_str)
    return float(value_str)
```

**Características:**
- ✅ **Funciona** con casos básicos
- ✅ **Demuestra** el concepto
- ⚠️ Puede tener TODOs
- ⚠️ Puede tener print() de debugging
- ⚠️ Manejo de errores básico

---

### Nivel 2: Versión "Demostrable" (Con Tests + Notebook)

**Objetivo**: Preparar para reunión con superior

```python
# tests/test_data_cleaner.py

def test_normalize_fortran_basic():
    """Test con casos mínimos para demostración"""
    assert normalize_fortran_scientific('.48430268-9') == 0.48430268e-9
    assert normalize_fortran_scientific('.10756032-8') == 0.10756032e-8
    assert normalize_fortran_scientific('0.817300E-05') == 0.817300e-5
```

**Notebook Demo:**
- Mostrar input original
- Mostrar output normalizado
- Comparación lado a lado
- Gráfico de % conversiones exitosas
- Validación con 100-1000 líneas reales

---

### Nivel 3: Versión "Pulida" (Main)

**Objetivo**: Código de producción

```python
# Después de feedback y validación
import re
import logging

def normalize_fortran_scientific(value_str: str) -> float:
    """
    Convierte la notación científica antigua de Fortran (usada por SACS) 
    a un número flotante (float) que Python pueda entender.
    """
    
    # 1. IMPORTACIÓN Y CONFIGURACIÓN DE LOGS
    # Usamos logging en lugar de print() para que en producción podamos 
    # rastrear errores sin llenar la pantalla de texto innecesario.
    logger = logging.getLogger(__name__)
    
    # 2. VALIDACIONES DE SEGURIDAD (GUARD CLAUSES)
    # Verificamos que lo que entra sea texto (str). Si es otra cosa, lanzamos un error.
    if not isinstance(value_str, str):
        raise TypeError(f"Esperaba str, recibió {type(value_str).__name__}")
    
    # Limpiamos espacios en blanco al inicio y final (muy común en archivos .txt)
    value_str = value_str.strip()
    
    # Si después de limpiar el string queda vacío, no podemos convertirlo.
    if not value_str:
        raise ValueError("String vacío no puede ser convertido")
    
    # Guardamos el valor original para reportarlo en caso de que ocurra un error.
    original = value_str
    
    # 3. NORMALIZACIÓN CON REGEX (EXPRESIONES REGULARES)
    # SACS ahorra espacio omitiendo la 'E'. Estos patrones detectan el signo 
    # pegado al número e inyectan la 'E' necesaria para Python.

    # Patrón 1: Casos como '.123-4' -> los convierte en '0.123E-4'
    # (\.\d+) captura el punto y dígitos; ([+-]) captura el signo; (\d+) captura el exponente.
    value_str = re.sub(r'(\.\d+)([+-])(\d+)', r'0\1E\2\3', value_str)
    
    # Patrón 2: Casos como '12.34-5' (sin la E) -> los convierte en '12.34E-5'
    value_str = re.sub(r'(\d+\.\d+)([+-])(\d+)', r'\1E\2\3', value_str)
    
    # Patrón 3: Casos de números enteros con exponente como '123+4' -> '123E+4'
    # ^ y $ aseguran que el patrón ocupe toda la cadena.
    value_str = re.sub(r'^(\d+)([+-])(\d+)$', r'\1E\2\3', value_str)
    
    # 4. INTENTO DE CONVERSIÓN Y MANEJO DE ERRORES
    try:
        # Intentamos la conversión final a número decimal.
        result = float(value_str)
        # Si funciona, guardamos un registro de éxito silencioso (debug).
        logger.debug(f"Convertido '{original}' → {result}")
        return result
        
    except ValueError as e:
        # Si float() falla (porque el texto no era un número válido), 
        # atrapamos ese error y lo guardamos en la variable 'e'.
        
        # Registramos el error en el sistema de logs para saber qué falló exactamente.
        logger.error(f"No se pudo convertir '{original}': {e}")
        
        # 'raise' lanza una nueva alerta personalizada.
        # 'from e' mantiene el historial del error original para que no se pierda la causa raíz.
        raise ValueError(f"Formato inválido: '{original}'") from e
```

**Características:**
- ✅ Docstrings completos
- ✅ Type hints
- ✅ Manejo robusto de errores
- ✅ Logging para debugging
- ✅ Validación de entrada
- ✅ Tests exhaustivos (20+ casos)

---

## 3. Estrategia de Ramas y Workflow

### Estructura de Branches

```
main (producción)
  │
  ├── etapa_1_limpieza_datos (desarrollo activo) ← ESTAMOS AQUÍ
  │   ├── feat/normalize_fortran
  │   ├── feat/detect_encoding
  │   └── feat/filter_lines
  │
  ├── etapa_2_parsing (siguiente)
  │
  └── etapa_3_consolidacion
```

---

### A) Trabajo Diario en Branch de Etapa

```bash
# Estás aquí ahora
git checkout etapa_1_limpieza_datos

# Implementar función
# Crear tests básicos
# Crear notebook demo
# Commit frecuentes (WIP está OK)

git add src/data_cleaner.py tests/test_data_cleaner.py
git commit -m "feat: agregar normalize_fortran_scientific (WIP)"

git add notebooks/demo_etapa1.ipynb
git commit -m "docs: notebook demo con validación inicial"
```

**Commits permitidos en branch de etapa:**
- `feat: ...` - Nueva funcionalidad
- `test: ...` - Agregar tests
- `docs: ...` - Documentación
- `wip: ...` - Trabajo en progreso
- `fix: ...` - Corrección de bugs

---

### B) Reunión con Superior (Demo en Branch)

#### Preparación (30 min antes)

```bash
# Activar entorno
mamba activate procesador_fatiga_sacs

# Asegurar que todo funciona
pytest tests/test_data_cleaner.py -v

# Abrir notebook demo
jupyter notebook notebooks/demo_etapa1.ipynb

# Generar reporte de cobertura (opcional)
pytest --cov=src --cov-report=html tests/
```

#### Durante la Reunión (15-20 min)

**Min 0-2: Contexto**
- "Etapa 1: Normalización de datos SACS"
- "Problema: notación Fortran no compatible con Python"
- "Solución: función de conversión automática"

**Min 2-5: Demostración en Vivo**
```python
# En notebook, ejecutar:
from src.data_cleaner import normalize_fortran_scientific

# Ejemplo simple
input_val = ".48430268-9"
output_val = normalize_fortran_scientific(input_val)
print(f"{input_val} → {output_val}")
# .48430268-9 → 4.8430268e-10 ✓
```

**Min 5-10: Validación con Datos Reales**
```python
# Cargar líneas de ftglstE1.txt
with open('data/ftglstE1.txt', 'r') as f:
    lines = [line for line in f if '*** TOTAL DAMAGE ***' in line][:100]

# Procesar valores
success = 0
failed = 0
for line in lines:
    values = line.split()[3:11]  # 8 valores de daño
    for val in values:
        try:
            normalize_fortran_scientific(val)
            success += 1
        except:
            failed += 1

print(f"Conversiones exitosas: {success}/{success+failed} ({success/(success+failed)*100:.1f}%)")
# Conversiones exitosas: 798/800 (99.8%) ✓
```

**Min 10-15: Tests Automatizados**
```bash
# En terminal, mostrar:
pytest tests/test_data_cleaner.py -v

# Output esperado:
# test_normalize_fortran_basic PASSED
# test_normalize_fortran_positive_exp PASSED
# test_normalize_fortran_standard PASSED
# test_normalize_invalid_format PASSED
# ======================== 4 passed in 0.12s ========================
```

**Min 15-20: Siguientes Pasos**
- "Con esto listo, puedo avanzar a las otras funciones"
- "Siguiente: detección de encoding"
- Solicitar feedback

#### Feedback Típico del Superior

✅ **Feedback constructivo:**
- "Agregar validación para valores extremadamente pequeños"
- "¿Qué pasa si el archivo tiene encoding Latin-1?"
- "Añadir log de líneas fallidas para debugging"
- "Probar con 10,000 líneas, no solo 100"

❌ **No esperado en esta etapa:**
- "Optimizar performance" (prematuro)
- "Agregar GUI" (es otra etapa)
- "Documentar todo el módulo" (se hará en refinamiento)

---

### C) Refinamiento Post-Feedback

```bash
# Aún en etapa_1_limpieza_datos
git checkout -b refactor/improve_normalize

# Implementar mejoras sugeridas
# 1. Agregar logging
# 2. Manejo de encoding
# 3. Validación de valores extremos
# 4. Tests con 10,000 casos

git add .
git commit -m "refactor: agregar logging y manejo de encoding"
git commit -m "test: expandir suite a 20 casos"
git commit -m "docs: actualizar docstrings con ejemplos"

# Merge a etapa_1_limpieza_datos
git checkout etapa_1_limpieza_datos
git merge refactor/improve_normalize

# Eliminar branch temporal
git branch -d refactor/improve_normalize
```

---

### D) Merge a Main (Código Pulido)

#### Criterios para Merge

**Checklist obligatorio:**
- [ ] **Todos los tests pasan** (cobertura > 80%)
- [ ] **Documentación completa** (docstrings, README actualizado)
- [ ] **Sin TODOs críticos** (pueden quedar TODOs de mejoras futuras)
- [ ] **Sin print() de debugging** (usar logging.debug())
- [ ] **Manejo robusto de errores**
- [ ] **Validado con datos reales** (10,000+ líneas)
- [ ] **Aprobación explícita del superior**
- [ ] **Código formateado** (black, flake8)

#### Proceso de Merge

```bash
# 1. Limpiar código
black src/
flake8 src/ --max-line-length=100

# 2. Verificación final
pytest --cov=src tests/ -v
# Cobertura esperada: > 80%

# 3. Actualizar README
# Marcar Etapa 1 como completada

# 4. Merge a main
git checkout main
git merge --no-ff etapa_1_limpieza_datos \
    -m "feat: Etapa 1 completada - Limpieza y normalización

- normalize_fortran_scientific(): Conversión de notación Fortran
- detect_file_encoding(): Detección automática de encoding
- is_valid_data_line(): Filtrado de líneas irrelevantes

Validado con 10,000+ líneas de ftglstE1.txt
Cobertura de tests: 85%
Aprobado por: [Nombre del Superior]"

# 5. Tag de versión
git tag -a v0.1.0 -m "Etapa 1: Limpieza y Normalización"

# 6. Push
git push origin main --tags
```

---

## 4. Estructura de Archivos para Demostración

```
etapa_1_limpieza_datos/
│
├── src/
│   ├── __init__.py
│   └── data_cleaner.py          # ★ 3 funciones principales
│       ├── normalize_fortran_scientific()
│       ├── detect_file_encoding()
│       └── is_valid_data_line()
│
├── tests/
│   ├── __init__.py
│   ├── test_data_cleaner.py     # Tests automatizados
│   └── fixtures/
│       └── sample_lines.txt     # 20-30 líneas de ejemplo
│
├── notebooks/
│   └── demo_etapa1.ipynb        # ★ PARA REUNIONES
│       ├── Sección 1: Problema
│       ├── Sección 2: Solución
│       ├── Sección 3: Pruebas visuales
│       ├── Sección 4: Validación con datos reales
│       └── Sección 5: Métricas de éxito
│
└── docs/
    └── implementacion_etapa_1.md  # Este documento
```

---

## 5. Implementación Incremental de Funciones

### Función 1: `normalize_fortran_scientific()`

#### Día 1 (Versión Alpha)
```python
def normalize_fortran_scientific(value_str):
    """Convierte .123-4 a 0.123E-04"""
    import re
    value_str = re.sub(r'(\.\d+)([+-])(\d+)', r'0\1E\2\3', value_str)
    return float(value_str)
```
- Test con 5 casos
- Maneja patrón básico `.123-4`

#### Día 2 (Versión Beta, post-demo)
```python
def normalize_fortran_scientific(value_str):
    """Convierte múltiples formatos Fortran"""
    import re
    # Maneja también 1.23-4 (sin punto inicial)
    value_str = re.sub(r'(\d+\.\d+)([+-])(\d+)', r'\1E\2\3', value_str)
    # Maneja .123+4 (exponentes positivos)
    value_str = re.sub(r'(\.\d+)([+-])(\d+)', r'0\1E\2\3', value_str)
    return float(value_str)
```
- Test con 20 casos
- Maneja exponentes positivos y negativos

#### Día 3 (Versión Release)
```python
def normalize_fortran_scientific(value_str: str) -> float:
    """Versión completa con validación y logging"""
    # [Código completo del Nivel 3]
    pass
```
- Test con 100 casos
- Manejo de errores completo
- Logging integrado

---

### Función 2: `detect_file_encoding()`

#### Día 1 (Versión Alpha)
```python
def detect_file_encoding(filepath):
    """Detecta encoding del archivo"""
    # Versión simple: intenta UTF-8, fallback Latin-1
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return 'utf-8'
    except:
        return 'latin-1'
```

#### Día 2 (Versión Release)
```python
def detect_file_encoding(filepath: str) -> str:
    """
    Detecta el encoding de un archivo SACS.
    
    Uses chardet library for automatic detection.
    Falls back to common encodings if detection fails.
    """
    import chardet
    
    with open(filepath, 'rb') as f:
        raw_data = f.read(10000)  # Leer primeros 10KB
    
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']
    
    # Fallback si confianza es baja
    if confidence < 0.7:
        encodings = ['utf-8', 'latin-1', 'windows-1252']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    f.read()
                return enc
            except:
                continue
    
    return encoding
```

---

### Función 3: `is_valid_data_line()`

#### Día 1 (Versión Alpha)
```python
def is_valid_data_line(line):
    """Filtra líneas irrelevantes"""
    # Versión simple
    if not line.strip():
        return False
    if 'SACS (2024)' in line:
        return False
    if 'FTG PAGE' in line:
        return False
    return True
```

#### Día 2 (Versión Release)
```python
def is_valid_data_line(line: str, context: str = None) -> bool:
    """
    Determina si una línea contiene datos relevantes.
    
    Args:
        line: Línea de texto a evaluar
        context: Contexto del parser (opcional)
        
    Returns:
        bool: True si la línea debe procesarse
    """
    import re
    
    # Líneas vacías
    if not line.strip():
        return False
    
    # Patrones de exclusión
    exclusion_patterns = [
        r'SACS \(\d{4}\)',              # Encabezado SACS
        r'FTG PAGE\s+\d+',              # Saltos de página
        r'^-+$',                        # Líneas de separación
        r'^\s+\*\*\*\s+[A-Z\s]+\*\*\*', # Encabezados de sección (excepto TOTAL DAMAGE)
        r'Company:\s+Company',          # Info de empresa
        r'DATE\s+\d{2}-[A-Z]{3}-\d{4}', # Timestamps
    ]
    
    for pattern in exclusion_patterns:
        if re.search(pattern, line):
            # Excepción: *** TOTAL DAMAGE *** es relevante
            if 'TOTAL DAMAGE' in line:
                return True
            return False
    
    return True
```

---

## 6. Contenido del Notebook Demo

### Estructura Sugerida

```python
# notebooks/demo_etapa1.ipynb

"""
# Demo Etapa 1: Limpieza y Normalización de Datos SACS

**Fecha**: 04/02/2026  
**Objetivo**: Demostrar funciones de normalización para notación Fortran

---

## 1. Problema Identificado

SACS genera reportes con notación científica Fortran que Python no puede leer:
"""

# Celda 1: Mostrar el problema
fortran_value = ".48430268-9"
try:
    float(fortran_value)
except ValueError as e:
    print(f"❌ Error: {e}")
    print(f"Python no puede convertir '{fortran_value}'")

"""
## 2. Solución Implementada
"""

# Celda 2: Import de función
import sys
sys.path.insert(0, '../src')
from data_cleaner import normalize_fortran_scientific

# Celda 3: Demostración simple
input_val = ".48430268-9"
output_val = normalize_fortran_scientific(input_val)
print(f"Input:  {input_val}")
print(f"Output: {output_val}")
print(f"Tipo:   {type(output_val)}")
print("✓ Conversión exitosa")

"""
## 3. Casos de Prueba
"""

# Celda 4: Múltiples casos
test_cases = [
    (".48430268-9", "Formato Fortran simple"),
    (".10756032-8", "Otro exponente negativo"),
    ("0.817300E-05", "Notación estándar"),
    (".123+4", "Exponente positivo"),
    ("1.23-4", "Sin punto inicial"),
]

print("Caso                  | Descripción                | Resultado")
print("-" * 70)
for val, desc in test_cases:
    try:
        result = normalize_fortran_scientific(val)
        print(f"{val:20s} | {desc:25s} | {result:.10e} ✓")
    except Exception as e:
        print(f"{val:20s} | {desc:25s} | ❌ {e}")

"""
## 4. Validación con Datos Reales
"""

# Celda 5: Cargar datos del archivo real
import re

with open('../data/ftglstE1.txt', 'r', encoding='latin-1') as f:
    lines = f.readlines()

# Extraer líneas con TOTAL DAMAGE
damage_lines = [line for line in lines if '*** TOTAL DAMAGE ***' in line]
print(f"Líneas con TOTAL DAMAGE encontradas: {len(damage_lines)}")

# Celda 6: Procesar valores
success = 0
failed = 0
failed_values = []

for line in damage_lines[:100]:  # Primeras 100 líneas
    values = line.split()[3:11]  # 8 valores de daño
    for val in values:
        try:
            normalize_fortran_scientific(val)
            success += 1
        except Exception as e:
            failed += 1
            failed_values.append((val, str(e)))

total = success + failed
print(f"\n📊 Resultados:")
print(f"  Conversiones exitosas: {success}/{total} ({success/total*100:.1f}%)")
print(f"  Conversiones fallidas: {failed}/{total} ({failed/total*100:.1f}%)")

if failed > 0:
    print(f"\n⚠️ Valores fallidos:")
    for val, error in failed_values[:5]:  # Mostrar primeros 5
        print(f"  - '{val}': {error}")

"""
## 5. Gráficos de Validación
"""

# Celda 7: Visualización
import matplotlib.pyplot as plt
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Gráfico 1: Tasa de éxito
ax1.pie([success, failed], labels=['Éxito', 'Fallo'], 
        autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#F44336'])
ax1.set_title('Tasa de Conversión')

# Gráfico 2: Distribución de magnitudes
converted_values = []
for line in damage_lines[:100]:
    values = line.split()[3:11]
    for val in values:
        try:
            converted_values.append(normalize_fortran_scientific(val))
        except:
            pass

log_values = [np.log10(abs(v)) if v != 0 else -20 for v in converted_values]
ax2.hist(log_values, bins=30, color='#2196F3', edgecolor='black')
ax2.set_xlabel('log10(Valor)')
ax2.set_ylabel('Frecuencia')
ax2.set_title('Distribución de Magnitudes')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

"""
## 6. Conclusiones

✅ **Logros**:
- Función implementada y funcional
- Tasa de conversión: 99.8%
- Validado con 800 valores reales

⏭️ **Siguientes pasos**:
- Implementar `detect_file_encoding()`
- Implementar `is_valid_data_line()`
- Expandir suite de tests a 50+ casos

---

**Fin de la demostración**
"""
```

---

## 7. Cronograma de Etapa 1

### Día 1 (Hoy)
- [x] Setup de entorno (mamba)
- [x] Crear estructura de carpetas
- [ ] Implementar `normalize_fortran_scientific()` v1
- [ ] Tests básicos (5 casos)
- [ ] Notebook demo inicial

### Día 2
- [ ] Reunión con superior (15 min)
- [ ] Incorporar feedback
- [ ] Implementar `detect_file_encoding()` v1
- [ ] Implementar `is_valid_data_line()` v1
- [ ] Expandir tests (20 casos)

### Día 3
- [ ] Refinar todas las funciones
- [ ] Validación con 10,000 líneas
- [ ] Documentación completa
- [ ] Cobertura de tests > 80%
- [ ] Preparar merge a main

---

## 8. Ventajas de Este Enfoque

### Para el Desarrollador (Tú)
✅ Avanzas rápido sin bloquearte en perfección prematura  
✅ Tienes código demostrable en 1-2 días  
✅ Recibes feedback temprano  
✅ Main siempre está "limpio" y deployable  
✅ Puedes experimentar libremente en branches  

### Para el Superior
✅ Ve progreso tangible cada semana  
✅ Puede probar el código en su máquina  
✅ Entiende qué funciona y qué falta  
✅ Puede sugerir cambios antes de merge a main  
✅ Tiene visibilidad completa del desarrollo  

### Para el Proyecto
✅ Riesgo reducido (iteraciones pequeñas)  
✅ Documentación se genera naturalmente (notebooks)  
✅ Código en main siempre es deployable  
✅ Historia de git clara y trazable  
✅ Fácil revertir cambios si algo falla  

---

## 9. Checklist Completo por Fase

### Antes de Reunión (Branch de Etapa)
- [ ] Función principal implementada y funcional
- [ ] 5-10 tests básicos (todos pasan)
- [ ] Notebook demo con resultados visuales
- [ ] Validación con subset de datos reales (100-1000 líneas)
- [ ] README actualizado con progreso
- [ ] Commit de código limpio

### Durante Reunión
- [ ] Activar entorno (`mamba activate procesador_fatiga_sacs`)
- [ ] Ejecutar tests (`pytest -v`)
- [ ] Abrir notebook demo
- [ ] Ejecutar celdas en vivo
- [ ] Mostrar validación con datos reales
- [ ] Tomar notas de feedback
- [ ] Acordar siguientes pasos

### Después de Reunión (Refinamiento)
- [ ] Implementar feedback del superior
- [ ] Expandir suite de tests (20+ casos)
- [ ] Agregar manejo de errores robusto
- [ ] Documentación completa (docstrings)
- [ ] Actualizar notebook con mejoras
- [ ] Sin TODOs críticos
- [ ] Logging implementado

### Antes de Merge a Main (Producción)
- [ ] Cobertura de tests > 80%
- [ ] Código formateado (`black src/`, `flake8 src/`)
- [ ] Sin warnings de linting
- [ ] Documentación revisada y completa
- [ ] README actualizado (marcar etapa completada)
- [ ] Aprobación explícita del superior
- [ ] Tag de versión creado (v0.1.0)

---

## 10. Comandos Git Útiles

```bash
# Ver estado actual
git status
git branch

# Ver diferencias antes de commit
git diff

# Commit con mensaje descriptivo
git add src/data_cleaner.py
git commit -m "feat: implementar normalize_fortran_scientific v1"

# Ver historial
git log --oneline --graph

# Crear sub-branch para experimentos
git checkout -b experiment/nueva-idea

# Volver a branch principal de etapa
git checkout etapa_1_limpieza_datos

# Actualizar desde main (si hubo cambios)
git fetch origin
git merge origin/main

# Ver diferencias con main
git diff main..etapa_1_limpieza_datos

# Preparar para merge
git checkout main
git merge --no-ff etapa_1_limpieza_datos
```

---

## 11. Resolución de Problemas Comunes

### Error: Tests no pasan

```bash
# Revisar output detallado
pytest tests/test_data_cleaner.py -v -s

# Ejecutar un test específico
pytest tests/test_data_cleaner.py::test_normalize_fortran_basic

# Ver coverage
pytest --cov=src --cov-report=term-missing tests/
```

### Error: Imports no funcionan en notebook

```python
# Agregar al inicio del notebook:
import sys
sys.path.insert(0, '../src')
```

### Error: Encoding del archivo

```bash
# Verificar encoding
file -i data/ftglstE1.txt

# Probar con diferentes encodings en Python:
encodings = ['utf-8', 'latin-1', 'windows-1252']
for enc in encodings:
    try:
        with open('data/ftglstE1.txt', 'r', encoding=enc) as f:
            f.read()
        print(f"✓ Funciona con: {enc}")
    except:
        print(f"❌ Falla con: {enc}")
```

---

## 12. Recursos y Referencias

### Documentación Interna
- [Dificultades Técnicas](dificultades_tecnicas.md)
- [Etapas del Proyecto](etapas_del_proyecto.md)
- [INSTALL.md](../INSTALL.md)

### Referencias Externas
- [Pytest Documentation](https://docs.pytest.org/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Black Formatter](https://black.readthedocs.io/)
- [Git Branching Strategies](https://www.atlassian.com/git/tutorials/comparing-workflows)

---

**Última actualización**: 04/02/2026  
**Versión**: 1.0  
**Próxima revisión**: Al completar Etapa 1
