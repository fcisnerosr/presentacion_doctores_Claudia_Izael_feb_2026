# Dificultades Técnicas - Procesador de Fatiga SACS v1.0

## Documento de Análisis Técnico

**Proyecto**: Procesador de Fatiga SACS v1.0  
**Fecha**: 04 de Febrero, 2026  
**Propósito**: Identificar, documentar y resolver los desafíos técnicos del parsing de archivos SACS FTG

---

## 🔴 DIFICULTADES CRÍTICAS

### 1. PARSING DE CAMPO MEMBER (Variable Format)

#### **¿Qué es?**
El campo MEMBER en los archivos SACS presenta múltiples formatos inconsistentes que dificultan su extracción confiable.

#### **¿Cómo se manifiesta?**
Ejemplos encontrados en el archivo:
```
JOINT   MEMBER      GRUP
0003    802L 0005   16A      ← Formato con espacio
0002    0002-501L   52A      ← Formato con guión
0002    401L-0002   52A      ← Formato invertido con guión
0003    802L-0003   DL9      ← Variante adicional
```

El campo MEMBER puede contener:
- Espacios internos (`802L 0005`)
- Guiones en diferentes posiciones (`0002-501L`, `401L-0002`)
- Longitud variable (9-11 caracteres)
- Combinaciones de números y letras sin patrón fijo

#### **¿Por qué es un problema?**
1. **Split por espacios falla**: Usar `line.split()` separaría `"802L 0005"` en dos campos distintos
2. **Posiciones fijas inciertas**: Sin conocer el ancho exacto de columna, el parsing por substring puede truncar datos
3. **Identificación única comprometida**: Si MEMBER se parsea incorrectamente, la llave única `JOINT_MEMBER_GRUP` será inválida
4. **Colisión de claves**: Parseos inconsistentes pueden generar claves duplicadas o faltantes al cruzar archivos

#### **¿Para qué necesitamos resolverlo?**
- **Integridad de datos**: MEMBER es parte de la llave única para identificar cada elemento estructural
- **Suma correcta entre archivos**: Si las claves son inconsistentes, los daños no se sumarán correctamente
- **Trazabilidad**: Los ingenieros necesitan identificar exactamente qué miembro estructural tiene qué daño acumulado

#### **Estrategia de solución**
```python
# Opción 1: Regex con grupos nombrados
pattern = r'^(?P<joint>\w+)\s+(?P<member>\S+(?:\s+\S+)?)\s+(?P<grup>\w+)'
match = re.match(pattern, line)
joint = match.group('joint')
member = match.group('member')
grup = match.group('grup')

# Opción 2: Columnas fijas (requiere validación en múltiples archivos)
joint = line[0:6].strip()
member = line[6:20].strip()  # Ancho aumentado para capturar espacios
grup = line[20:25].strip()

# Opción 3: Split inteligente
parts = line.split()
joint = parts[0]
grup = parts[-1]  # Último elemento siempre es GRUP
member = ' '.join(parts[1:-1])  # Todo lo que está entre JOINT y GRUP
```

**Validación necesaria**: Comparar resultados de las tres técnicas en 100 líneas aleatorias del archivo.

---

### 2. NOTACIÓN CIENTÍFICA FORTRAN (Sin "E" explícita)

#### **¿Qué es?**
SACS exporta números en notación científica Fortran donde el exponente se escribe sin la letra "E" y sin el "0" inicial, causando que Python no pueda convertirlos a `float()`.

#### **¿Cómo se manifiesta?**
Ejemplos encontrados:
```
FORMATO FORTRAN              FORMATO ESPERADO
.48430268-9                  0.48430268E-9
.10756032-8                  0.10756032E-8
.58233452-8                  0.58233452E-8
```

Patrón identificado: `.<dígitos><signo><exponente>`

#### **¿Por qué es un problema?**
1. **Error de conversión**: Python lanza `ValueError: could not convert string to float: '.48430268-9'`
2. **Distribución masiva**: Encontrado en más de 20 ocurrencias en la sección "MEMBER LOAD-CASE DAMAGE REPORT" (línea 93050+)
3. **Pérdida de datos**: Sin normalización, todos los valores en formato Fortran se perderían
4. **Coexistencia de formatos**: En el mismo archivo hay valores en formato estándar (`0.817300E-05`) y Fortran (`.48430268-9`)

#### **¿Para qué necesitamos resolverlo?**
- **Cálculos numéricos**: Los valores de daño deben convertirse a float para sumarlos aritméticamente
- **Precisión**: Los valores de fatiga son típicamente muy pequeños (1E-7 a 1E-10), cualquier pérdida de precisión es inaceptable
- **Compatibilidad**: Pandas y NumPy requieren tipos numéricos válidos para operaciones

#### **Estrategia de solución**
```python
import re

def normalize_fortran_scientific(value_str):
    """
    Convierte notación científica Fortran a formato Python estándar.
    
    Transformaciones:
    - .123-4  → 0.123E-04
    - .123+4  → 0.123E+04
    - 1.23-4  → 1.23E-04  (caso adicional sin 0 inicial)
    
    Args:
        value_str (str): Valor en formato Fortran
        
    Returns:
        float: Valor numérico convertido
    """
    # Caso 1: .dígitos-exponente o .dígitos+exponente
    value_str = re.sub(r'(\.\d+)([+-])(\d+)', r'0\1E\2\3', value_str)
    
    # Caso 2: dígitos.dígitos-exponente (sin E)
    value_str = re.sub(r'(\d+\.\d+)([+-])(\d+)', r'\1E\2\3', value_str)
    
    # Caso 3: dígitos-exponente (entero sin decimal)
    value_str = re.sub(r'(\d+)([+-])(\d+)$', r'\1E\2\3', value_str)
    
    try:
        return float(value_str)
    except ValueError as e:
        raise ValueError(f"No se pudo convertir '{value_str}' después de normalización: {e}")

# Aplicación en línea de datos
damage_values = []
for value_str in line.split()[4:12]:  # 8 valores de daño por línea
    normalized_value = normalize_fortran_scientific(value_str)
    damage_values.append(normalized_value)
```

**Casos de prueba**:
```python
assert normalize_fortran_scientific('.48430268-9') == 0.48430268e-9
assert normalize_fortran_scientific('.10756032-8') == 0.10756032e-8
assert normalize_fortran_scientific('0.817300E-05') == 0.817300e-5
```

---

### 3. SUMA ARITMÉTICA ENTRE MÚLTIPLES ARCHIVOS

#### **¿Qué es?**
SACS genera un archivo de fatiga por etapa temporal (ej. años 0-10, 10-20, 20-30). El software **NO** suma automáticamente el daño acumulado entre modelos, por lo que debemos hacerlo manualmente.

#### **¿Cómo se manifiesta?**
Estructura de archivos de entrada:
```
data/
  ├── ftglstE1.txt  (años 0-10)
  ├── ftglstE2.txt  (años 10-20)
  └── ftglstE3.txt  (años 20-30)
```

Cada archivo contiene:
```
JOINT  MEMBER    GRUP    TOP      TOP-LEFT  ...  TOP-RIGHT
0003   802L 0005  16A   0.00081   0.00073   ...  0.00036
```

Salida esperada (suma):
```
JOINT  MEMBER    GRUP    TOP           TOP-LEFT      ...
0003   802L 0005  16A   0.00081*3     0.00073*3     ...  (suma de 3 archivos)
```

#### **¿Por qué es un problema?**
1. **Claves inconsistentes**: Si un elemento aparece en E1 pero no en E2, la suma debe manejar valores faltantes
2. **Orden de archivos**: El usuario puede seleccionar archivos en cualquier orden
3. **Volumen de datos**: Con ~2000 elementos por archivo × 3 archivos = 6000 registros a consolidar
4. **Validación de integridad**: ¿Qué hacer si un JOINT-MEMBER aparece en E1 pero no en E3?

#### **¿Para qué necesitamos resolverlo?**
- **Requisito central del negocio**: El objetivo del software ES sumar daños entre etapas
- **Cumplimiento normativo**: Los códigos de diseño (API RP-2A, DNV) requieren daño acumulado total
- **Decisiones de ingeniería**: Los ingenieros necesitan saber si un elemento excede el límite de vida útil (damage > 1.0)

#### **Estrategia de solución**
```python
from collections import defaultdict
import pandas as pd
import numpy as np

def process_multiple_files(file_paths, progress_callback=None):
    """
    Procesa múltiples archivos SACS y suma daños acumulados.
    
    Args:
        file_paths (list): Lista de rutas de archivos .txt
        progress_callback (callable): Función para actualizar barra de progreso
        
    Returns:
        pd.DataFrame: DataFrame con daños consolidados
    """
    # Estructura: {(joint, member, grup): [top, top_left, ..., top_right]}
    accumulated_damage = defaultdict(lambda: np.zeros(8, dtype=np.float64))
    
    total_files = len(file_paths)
    
    for i, filepath in enumerate(file_paths):
        # Parsear archivo individual
        file_data = parse_fatigue_file(filepath)
        
        # Acumular daños
        for key, damages in file_data.items():
            accumulated_damage[key] += damages
        
        # Actualizar progreso
        if progress_callback:
            progress_callback(i + 1, total_files)
    
    # Convertir a DataFrame
    df = pd.DataFrame.from_dict(
        accumulated_damage,
        orient='index',
        columns=['TOP', 'TOP-LEFT', 'LEFT', 'BOT-LEFT', 
                'BOT', 'BOT-RIGHT', 'RIGHT', 'TOP-RIGHT']
    )
    
    # Extraer JOINT, MEMBER, GRUP del índice
    df.reset_index(inplace=True)
    df[['JOINT', 'MEMBER', 'GRUP']] = df['index'].str.split('_', n=2, expand=True)
    df.drop('index', axis=1, inplace=True)
    
    # Calcular daño máximo por fila
    damage_columns = ['TOP', 'TOP-LEFT', 'LEFT', 'BOT-LEFT', 
                     'BOT', 'BOT-RIGHT', 'RIGHT', 'TOP-RIGHT']
    df['MAX_DAMAGE'] = df[damage_columns].max(axis=1)
    df['CRITICAL_LOCATION'] = df[damage_columns].idxmax(axis=1)
    
    # Ordenar por daño máximo (descendente)
    df.sort_values('MAX_DAMAGE', ascending=False, inplace=True)
    
    return df

# Manejo de elementos faltantes
# Si un elemento NO aparece en un archivo, su contribución es 0 (comportamiento de defaultdict)
# Esto es correcto: si no está en el modelo, no aporta daño en esa etapa
```

**Validación**: Comparar suma manual de 5 elementos contra resultado del software.

---

### 4. LÓGICA DE ESTADO MULTILÍNEA (State Machine)

#### **¿Qué es?**
Cada bloque de datos de un elemento estructural se distribuye en **18 líneas**:
- 1 línea de encabezado (JOINT, MEMBER, GRUP, LOAD CASE 1)
- 15 líneas adicionales (LOAD CASE 2-16)
- 1 línea de resumen (`*** TOTAL DAMAGE ***`)

#### **¿Cómo se manifiesta?**
```
Línea N:   0003  802L 0005  16A   1  0.00993  0.01582  ...
Línea N+1:                         2  0.02721  0.04682  ...
Línea N+2:                         3  0.16695  0.22870  ...
...
Línea N+15:                       16  0.03047  0.03275  ...
Línea N+16:    *** TOTAL DAMAGE ***   0.817E-05 0.727E-05 ...
```

No hay un marcador claro de fin de bloque **excepto** la línea `*** TOTAL DAMAGE ***`.

#### **¿Por qué es un problema?**
1. **Parser secuencial**: Debemos mantener estado entre líneas para saber si estamos leyendo casos de carga o el total
2. **Saltos de página**: Los encabezados de página pueden aparecer **dentro** de un bloque de 18 líneas
3. **Detección de inicio**: ¿Cómo saber cuándo inicia un nuevo bloque? (JOINT en columna 0)
4. **Bloques incompletos**: ¿Qué hacer si un archivo termina sin la línea `*** TOTAL DAMAGE ***`?

#### **¿Para qué necesitamos resolverlo?**
- **Extracción correcta**: Solo la línea `*** TOTAL DAMAGE ***` contiene los valores que debemos sumar
- **Robustez**: El parser no debe "perderse" si hay líneas inesperadas
- **Debugging**: Saber en qué estado está el parser ayuda a diagnosticar errores

#### **Estrategia de solución**
```python
from enum import Enum

class ParserState(Enum):
    SEARCHING = 1      # Buscando inicio de sección MEMBER FATIGUE REPORT
    READING_HEADER = 2 # Leyendo encabezado de columnas
    READING_CASES = 3  # Leyendo 16 casos de carga
    READING_TOTAL = 4  # Esperando línea *** TOTAL DAMAGE ***

def parse_fatigue_file(filepath):
    """
    Parser con máquina de estados para archivos SACS FTG.
    """
    state = ParserState.SEARCHING
    current_key = None
    current_cases = []
    results = {}
    
    with open(filepath, 'r', encoding='latin-1') as f:
        for line_num, line in enumerate(f, start=1):
            
            # Ignorar líneas de encabezado/página
            if 'SACS (2024)' in line or 'FTG PAGE' in line:
                continue
            
            # Estado: Buscando sección
            if state == ParserState.SEARCHING:
                if 'MEMBER FATIGUE DETAIL REPORT' in line:
                    state = ParserState.READING_HEADER
                    continue
            
            # Estado: Leyendo encabezado de columnas
            elif state == ParserState.READING_HEADER:
                if 'JOINT' in line and 'MEMBER' in line and 'GRUP' in line:
                    state = ParserState.READING_CASES
                    continue
            
            # Estado: Leyendo casos de carga
            elif state == ParserState.READING_CASES:
                # ¿Es inicio de nuevo bloque? (JOINT en columna 0)
                if line[0:6].strip() and not line.strip().startswith('***'):
                    # Extraer JOINT, MEMBER, GRUP
                    parts = line.split()
                    joint = parts[0]
                    grup = parts[-9]  # GRUP está 9 posiciones antes del final
                    member = ' '.join(parts[1:-9])
                    current_key = f"{joint}_{member}_{grup}"
                    current_cases = []
                
                # ¿Es línea *** TOTAL DAMAGE ***?
                if '*** TOTAL DAMAGE ***' in line:
                    # Extraer 8 valores de daño
                    values = line.split()[3:11]  # Después de "*** TOTAL DAMAGE ***"
                    damage_array = np.array([
                        normalize_fortran_scientific(v) for v in values
                    ])
                    results[current_key] = damage_array
                    current_key = None
    
    return results
```

**Mejora futura**: Añadir logging para diagnosticar bloques incompletos.

---

## 🟡 DIFICULTADES MEDIAS

### 5. MÚLTIPLES REGISTROS POR JOINT (Relación 1:N)

#### **¿Qué es?**
Un mismo JOINT puede tener múltiples MEMBER asociados (conexiones estructurales).

#### **¿Cómo se manifiesta?**
```
JOINT  MEMBER       GRUP
0003   802L 0005    16A     ← Conexión 1
0003   0003-0005    16A     ← Conexión 2
0003   802L-0003    DL9     ← Conexión 3
```

#### **¿Por qué es un problema?**
Si usamos solo `JOINT` como clave primaria, sobrescribiremos registros.

#### **¿Para qué necesitamos resolverlo?**
Cada conexión tiene su propio daño acumulado independiente. Perder registros significa pérdida de información crítica de seguridad estructural.

#### **Solución**
Usar clave compuesta: `JOINT + MEMBER + GRUP`

```python
key = f"{joint}_{member}_{grup}"
```

---

### 6. ARCHIVOS GRANDES (Performance)

#### **¿Qué es?**
El archivo de prueba tiene **146,370 líneas** (~12 MB). Archivos de producción pueden ser mucho mayores.

#### **¿Por qué es un problema?**
- Cargar todo en memoria puede causar `MemoryError`
- Procesamiento lento afecta experiencia de usuario
- GUI puede "congelarse" sin multi-threading

#### **¿Para qué necesitamos resolverlo?**
La aplicación debe procesar múltiples archivos grandes en tiempo razonable (<30 segundos para 3 archivos de 150k líneas).

#### **Solución**
```python
# 1. Procesamiento línea por línea (streaming)
def parse_fatigue_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:  # No carga todo en RAM
            process_line(line)

# 2. Threading para GUI
from threading import Thread

def process_files_threaded(files, callback):
    thread = Thread(target=process_files, args=(files, callback))
    thread.start()
```

---

## 🟢 DIFICULTADES BAJAS

### 7. SALTOS DE PÁGINA

#### **¿Qué es?**
Encabezados repetitivos cada ~50 líneas:
```
SACS (2024)                         FTG PAGE  810
* *  M E M B E R  F A T I G U E  D E T A I L  R E P O R T  * *
```

#### **Solución**
```python
if 'SACS (2024)' in line or 'FTG PAGE' in line:
    continue
```

---

### 8. ESPACIOS EN BLANCO VARIABLES

#### **¿Qué es?**
Separación de valores con espacios de longitud variable.

#### **Solución**
```python
values = line.split()  # Divide por cualquier whitespace
```

---

## Matriz de Riesgo

| Dificultad | Impacto | Probabilidad | Prioridad |
|------------|---------|--------------|-----------|
| Parsing MEMBER | Alto | Alta | P0 |
| Notación Fortran | Alto | Alta | P0 |
| Suma entre archivos | Alto | Alta | P0 |
| State Machine | Medio | Media | P1 |
| Múltiples registros | Medio | Alta | P1 |
| Archivos grandes | Medio | Media | P2 |
| Saltos de página | Bajo | Alta | P3 |
| Espacios variables | Bajo | Baja | P3 |

---

## Recomendaciones de Testing

1. **Unit Tests**: Crear casos de prueba para cada función de parsing
2. **Integration Tests**: Probar suma de 2-3 archivos reales
3. **Edge Cases**: Archivos vacíos, bloques incompletos, valores extremos
4. **Performance Tests**: Medir tiempo con archivos de 200k+ líneas
5. **Validation**: Comparar resultados contra cálculo manual en Excel

---

**Documento generado**: 04/02/2026  
**Revisión**: v1.0  
**Autor**: Análisis técnico automatizado
