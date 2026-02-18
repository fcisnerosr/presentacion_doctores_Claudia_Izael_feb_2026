# Output Provisional por Etapa

Este directorio contiene archivos de salida provisionales generados en cada etapa del desarrollo para validación y verificación.

---

## 📂 Contenido

### Etapa 1: Limpieza y Normalización
- **`ftglstE1_etapa1.txt`**: Archivo ftglstE1.txt con notación Fortran convertida a notación estándar Python
  - Valores `.123-4` convertidos a `1.23000000E-04`
  - Encoding convertido de Latin-1 a UTF-8
  - **Propósito**: Validar que la función `normalize_fortran_scientific()` funciona correctamente en todo el archivo

### Etapa 2: Parsing y Extracción ✅ COMPLETADA
- **`ftglstE1_etapa2.csv`**: Archivo CSV con elementos estructurados extraídos

**El CSV extrae y estructura** la información clave del archivo SACS en **una tabla**:

```
Archivo Original → 404L_0426 J491_24B (multi-línea, 20+ líneas por elemento)
CSV Estructurado → Una fila con: JOINT, MEMBER, GRUP, 8 daños, MAX_DAMAGE
```

**Ventajas**:
- ✅ **Una fila = un elemento estructural** (fácil de leer)
- ✅ **Ordenado por daño máximo** (críticos primero)  
- ✅ **Fácil de filtrar y analizar** en Excel/LibreOffice
- ✅ **Listo para sumar** con otros archivos (Etapa 3)

**Contenido**:
  - 350 elementos encontrados (JOINT + MEMBER + GRUP)
  - 8 valores de daño por elemento (TOP, TOP-LEFT, LEFT, BOT-LEFT, BOT, BOT-RIGHT, RIGHT, TOP-RIGHT)
  - Ordenados por daño máximo (descendente)
  - Columnas: JOINT, MEMBER, GRUP, TOP, TOP-LEFT, LEFT, BOT-LEFT, BOT, BOT-RIGHT, RIGHT, TOP-RIGHT, MAX_DAMAGE, CRITICAL_LOCATION, UNIQUE_KEY
  - **Propósito**: Validar extracción correcta de datos estructurados con máquina de estados

### Etapa 3: Consolidación y Suma (Pendiente)
- **`consolidado_etapa3.csv`**: Resultado de suma de múltiples archivos
  - Daño acumulado por elemento
  - **Propósito**: Validar lógica de agregación

### Etapa 5: Exportación Final (Pendiente)
- **`resultado_final.xlsx`**: Archivo Excel profesional para entrega

---

## ⚠️ Importante

**Estos archivos son PROVISIONALES y NO deben usarse en producción.**

Su único propósito es:
- ✅ Validación durante desarrollo
- ✅ Verificación de cada etapa
- ✅ Comparación entre etapas
- ✅ Debug y troubleshooting

**NO incluir en:**
- ❌ Entregas finales
- ❌ Control de versiones (Git)
- ❌ Backups de producción

---

## 🧹 Limpieza

Para eliminar archivos provisionales:
```bash
rm output_provisional/ftglstE1_etapa*.txt
```

---

**Última actualización**: Etapa 1 completada (10/02/2026)
