"""
Módulo de Limpieza y Normalización de Datos SACS
Etapa 1: Procesador de Fatiga SACS v1.0

Este módulo proporciona funciones para normalizar y limpiar datos
crudos extraídos de archivos de reporte de fatiga SACS.
"""

import re
import logging
from typing import Optional

# Configurar logging
logger = logging.getLogger(__name__)


def normalize_fortran_scientific(value_str: str) -> float:
    """
    Convierte la notación científica antigua de Fortran (usada por SACS) 
    a un número flotante (float) que Python pueda entender.
    
    SACS omite la letra 'E' en la notación científica para ahorrar espacio,
    lo que causa que Python no pueda convertir estos valores directamente.
    
    Transformaciones:
        '.48430268-9'  → 0.48430268E-09  → 4.8430268e-10
        '.10756032-8'  → 0.10756032E-08  → 1.0756032e-09
        '1.23-4'       → 1.23E-04        → 0.000123
        '.123+4'       → 0.123E+04       → 1230.0
        '0.817300E-05' → 0.817300E-05    → 8.173e-06 (ya está en formato correcto)
    
    Args:
        value_str: String con valor en formato Fortran
        
    Returns:
        float: Valor numérico convertido
        
    Raises:
        TypeError: Si el argumento no es un string
        ValueError: Si el string no puede ser convertido a float
        
    Examples:
        >>> normalize_fortran_scientific('.48430268-9')
        4.8430268e-10
        >>> normalize_fortran_scientific('0.817300E-05')
        8.173e-06
    """
    # Validación de entrada
    if not isinstance(value_str, str):
        raise TypeError(f"Esperaba str, recibió {type(value_str).__name__}")
    
    # Limpiar espacios en blanco
    value_str = value_str.strip()
    
    if not value_str:
        raise ValueError("String vacío no puede ser convertido")
    
    # Guardar valor original para reportes de error
    original = value_str
    
    # NORMALIZACIÓN CON REGEX
    # IMPORTANTE: El orden de los patrones es crítico para evitar doble sustitución
    
    # Patrón 1: dígitos.dígitos±exponente → dígitos.dígitosE±exponente
    # Ejemplo: 1.23-4 → 1.23E-4
    # Este debe ir PRIMERO para capturar números con parte entera
    value_str = re.sub(r'^(\d+\.\d+)([+-])(\d+)$', r'\1E\2\3', value_str)
    
    # Patrón 2: .dígitos±exponente → 0.dígitosE±exponente
    # Ejemplo: .123-4 → 0.123E-4
    # Este va segundo para capturar números que empiezan con punto
    value_str = re.sub(r'^(\.\d+)([+-])(\d+)$', r'0\1E\2\3', value_str)
    # Patrón 3: dígitos±exponente → dígitosE±exponente (números enteros)
    # Ejemplo: 123-4 → 123E-4
    value_str = re.sub(r'^(\d+)([+-])(\d+)$', r'\1E\2\3', value_str)
    
    # Intento de conversión
    try:
        result = float(value_str)
        logger.debug(f"Convertido '{original}' → {result}")
        return result
        
    except ValueError as e:
        logger.error(f"No se pudo convertir '{original}': {e}")
        raise ValueError(f"Formato inválido: '{original}'") from e


def detect_file_encoding(filepath: str) -> str:
    """
    Detecta el encoding de un archivo SACS.
    
    SACS puede generar archivos en diferentes encodings dependiendo de:
    - Versión del software
    - Sistema operativo donde se ejecutó
    - Configuración regional
    
    Este método utiliza la librería chardet para detección automática,
    con fallback a encodings comunes si la detección falla.
    
    Args:
        filepath: Ruta al archivo .txt de SACS
        
    Returns:
        str: Nombre del encoding detectado ('utf-8', 'latin-1', 'windows-1252', etc.)
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        
    Examples:
        >>> encoding = detect_file_encoding('data/ftglstE1.txt')
        >>> print(encoding)
        'utf-8'
    """
    try:
        import chardet
        
        # Leer primeros 10KB para análisis
        with open(filepath, 'rb') as f:
            raw_data = f.read(10000)
        
        # Detectar encoding
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        
        logger.debug(f"Encoding detectado: {encoding} (confianza: {confidence:.2%})")
        
        # Si la confianza es baja, intentar encodings comunes
        if confidence < 0.7:
            logger.warning(f"Baja confianza en detección ({confidence:.2%}), probando encodings comunes")
            encodings = ['utf-8', 'latin-1', 'windows-1252', 'ascii']
            
            for enc in encodings:
                try:
                    with open(filepath, 'r', encoding=enc) as f:
                        f.read()
                    logger.info(f"Encoding válido encontrado: {enc}")
                    return enc
                except (UnicodeDecodeError, UnicodeError):
                    continue
        
        return encoding if encoding else 'utf-8'
        
    except ImportError:
        # Si chardet no está disponible, usar método simple
        logger.warning("chardet no disponible, usando detección simple")
        
        # Intentar UTF-8 primero
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read()
            return 'utf-8'
        except UnicodeDecodeError:
            # Fallback a Latin-1 (acepta todos los bytes)
            return 'latin-1'


def is_valid_data_line(line: str, context: Optional[str] = None) -> bool:
    """
    Determina si una línea contiene datos relevantes o debe ser filtrada.
    
    Los archivos SACS contienen:
    - Líneas de datos de fatiga (RELEVANTES)
    - Encabezados de página (FILTRAR)
    - Saltos de página (FILTRAR)
    - Líneas de separación (FILTRAR)
    - Líneas vacías (FILTRAR)
    
    Criterios de exclusión:
    - Líneas vacías o solo espacios en blanco
    - Líneas con "SACS (año)" - encabezados de página
    - Líneas con "FTG PAGE" - numeración de página
    - Líneas de separación (solo guiones)
    - Encabezados de sección (*** TITLE ***)
    - Información de empresa/fecha
    
    Excepciones importantes:
    - "*** TOTAL DAMAGE ***" es RELEVANTE (contiene los valores a procesar)
    
    Args:
        line: Línea de texto del archivo a evaluar
        context: Contexto opcional del parser (reservado para uso futuro)
        
    Returns:
        bool: True si la línea debe procesarse, False si debe filtrarse
        
    Examples:
        >>> is_valid_data_line("")
        False
        >>> is_valid_data_line("SACS (2024)                         FTG PAGE  810")
        False
        >>> is_valid_data_line("   *** TOTAL DAMAGE ***   0.817E-05 0.727E-05")
        True
        >>> is_valid_data_line("0003  802L 0005  16A   1  .48430268-9")
        True
    """
    # Líneas vacías
    if not line.strip():
        return False
    
    # Patrones de exclusión
    exclusion_patterns = [
        r'SACS\s*\(\d{4}\)',              # Encabezado SACS (año)
        r'FTG\s+PAGE\s+\d+',              # Saltos de página
        r'^[-\s]+$',                      # Líneas de solo guiones/espacios
        r'Company:\s*\w+',                # Info de empresa
        r'DATE\s+\d{2}-[A-Z]{3}-\d{4}',   # Timestamps
        r'TIME\s+\d{2}:\d{2}:\d{2}',      # Timestamps
        r'JOINT\s+MEMBER\s+GRUP',         # Encabezado de columnas
        r'FATG\s+TOP\s+TOP-LEFT',         # Encabezado de columnas
        r'^\s*\*\s+\*\s+[A-Z\s]+\*\s+\*\s*$',  # Títulos con formato * * T I T L E * *
    ]
    
    # Verificar cada patrón de exclusión
    for pattern in exclusion_patterns:
        if re.search(pattern, line):
            return False
    
    # Patrón especial para encabezados de sección genéricos (ej: *** TITLE ***)
    # PERO permitir *** TOTAL DAMAGE *** que es relevante
    if re.search(r'^\s*\*{3}\s+[A-Z\s]+\*{3}\s*$', line):
        # EXCEPCIÓN: *** TOTAL DAMAGE *** es relevante
        if 'TOTAL DAMAGE' not in line:
            return False
    
    # Si no coincide con patrones de exclusión, es válida
    return True
