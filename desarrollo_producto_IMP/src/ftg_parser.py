"""
Parser de Archivos SACS FTG - Etapa 2: Parsing y Extracción
Procesador de Fatiga SACS v1.0

Parser con máquina de estados para extraer datos estructurados de archivos SACS.
"""

import re
import logging
from enum import Enum
from typing import Optional, List
import numpy as np

from data_cleaner import normalize_fortran_scientific, is_valid_data_line, detect_file_encoding
from models import FatigueElement, ParseResult

# Configurar logging
logger = logging.getLogger(__name__)


class ParserState(Enum):
    """Estados de la máquina de parsing."""
    SEARCHING = 1        # Buscando sección MEMBER FATIGUE DETAIL REPORT
    READING_HEADER = 2   # Leyendo encabezado de columnas
    READING_ELEMENT = 3  # Leyendo datos de un elemento
    READING_TOTAL = 4    # Leyendo línea *** TOTAL DAMAGE ***


class FTGParser:
    """
    Parser de archivos SACS FTG con máquina de estados.
    
    Extrae elementos estructurales con sus valores de daño de fatiga.
    """
    
    def __init__(self):
        """Inicializa el parser."""
        self.state = ParserState.SEARCHING
        self.current_element = None
        self.elements = {}
        self.errors = []
        self.warnings = []
        self.line_number = 0
    
    def parse_file(self, filepath: str) -> ParseResult:
        """
        Parsea un archivo SACS FTG completo.
        
        Args:
            filepath: Ruta al archivo .txt de SACS
            
        Returns:
            ParseResult: Resultado del parsing con elementos extraídos
        """
        logger.info(f"Iniciando parsing de: {filepath}")
        
        # Detectar encoding
        try:
            encoding = detect_file_encoding(filepath)
            logger.debug(f"Encoding detectado: {encoding}")
        except Exception as e:
            logger.warning(f"Error detectando encoding, usando latin-1: {e}")
            encoding = 'latin-1'
        
        # Reiniciar estado
        self._reset()
        
        # Procesar archivo línea por línea
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                for line in f:
                    self.line_number += 1
                    self._process_line(line)
            
            logger.info(f"Parsing completado: {len(self.elements)} elementos extraídos")
            
        except Exception as e:
            error_msg = f"Error crítico leyendo archivo: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
        
        # Retornar resultado
        return ParseResult(
            elements=self.elements,
            total_elements=len(self.elements),
            errors=self.errors,
            warnings=self.warnings
        )
    
    def _reset(self):
        """Reinicia el estado del parser."""
        self.state = ParserState.SEARCHING
        self.current_element = None
        self.elements = {}
        self.errors = []
        self.warnings = []
        self.line_number = 0
    
    def _process_line(self, line: str):
        """
        Procesa una línea según el estado actual.
        
        Args:
            line: Línea del archivo
        """
        # Filtrar líneas irrelevantes
        if not is_valid_data_line(line):
            return
        
        # Máquina de estados
        if self.state == ParserState.SEARCHING:
            self._handle_searching(line)
        elif self.state == ParserState.READING_HEADER:
            self._handle_reading_header(line)
        elif self.state == ParserState.READING_ELEMENT:
            self._handle_reading_element(line)
        elif self.state == ParserState.READING_TOTAL:
            self._handle_reading_total(line)
    
    def _handle_searching(self, line: str):
        """Busca la sección MEMBER FATIGUE DETAIL REPORT."""
        if 'MEMBER FATIGUE DETAIL REPORT' in line or 'M E M B E R  F A T I G U E  D E T A I L  R E P O R T' in line:
            logger.debug(f"Encontrada sección en línea {self.line_number}")
            self.state = ParserState.READING_HEADER
    
    def _handle_reading_header(self, line: str):
        """Espera el encabezado de columnas para empezar a leer elementos."""
        # Buscar línea con encabezado de columnas
        if 'JOINT' in line and 'GRUP' in line and 'DAMAGES' in line:
            logger.debug(f"Encontrado encabezado en línea {self.line_number}")
            self.state = ParserState.READING_ELEMENT
    
    def _handle_reading_element(self, line: str):
        """Lee datos de elementos estructurales."""
        # Verificar si es línea *** TOTAL DAMAGE ***
        if '*** TOTAL DAMAGE ***' in line:
            self.state = ParserState.READING_TOTAL
            self._handle_reading_total(line)
            return
        
        # Intentar extraer identificadores (JOINT, MEMBER, GRUP)
        identifiers = self._extract_identifiers(line)
        if identifiers:
            self.current_element = identifiers
            logger.debug(f"Elemento encontrado: {identifiers}")
    
    def _handle_reading_total(self, line: str):
        """Lee línea *** TOTAL DAMAGE *** y crea el elemento."""
        if '*** TOTAL DAMAGE ***' not in line:
            # Volver a buscar elementos
            self.state = ParserState.READING_ELEMENT
            return
        
        if not self.current_element:
            self.warnings.append(f"Línea {self.line_number}: *** TOTAL DAMAGE *** sin elemento previo")
            self.state = ParserState.READING_ELEMENT
            return
        
        # Extraer valores de daño
        try:
            damages = self._extract_damages(line)
            
            # Crear elemento
            element = FatigueElement(
                joint=self.current_element['joint'],
                member=self.current_element['member'],
                grup=self.current_element['grup'],
                damages=damages
            )
            
            # Guardar en diccionario
            self.elements[element.unique_key] = element
            logger.debug(f"Elemento guardado: {element.unique_key}")
            
        except Exception as e:
            error_msg = f"Línea {self.line_number}: Error procesando TOTAL DAMAGE: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
        
        # Volver a buscar elementos
        self.current_element = None
        self.state = ParserState.READING_ELEMENT
    
    def _extract_identifiers(self, line: str) -> Optional[dict]:
        """
        Extrae JOINT, MEMBER (CHD+BRC), GRUP de una línea.
        
        Formato esperado: JOINT  CHD  BRC  GRUP  LOAD  valores...
        Ejemplo: 0003  802L 0005  16A  14   valores...
        
        Args:
            line: Línea de datos
            
        Returns:
            dict con ['joint', 'member', 'grup'] o None si no se encuentra
        """
        # La línea debe empezar con un número (JOINT)
        line = line.strip()
        if not line or not line[0].isdigit():
            return None
        
        # Intentar split
        parts = line.split()
        
        if len(parts) < 4:  # Al menos: JOINT CHD BRC GRUP
            return None
        
        try:
            # JOINT: primer elemento
            joint = parts[0]
            
            # Buscar GRUP: elemento alfanumérico de 2-4 caracteres
            # que aparece antes de un número (LOAD)
            grup_idx = None
            for i in range(1, min(len(parts), 6)):  # Buscar en primeras posiciones
                part = parts[i]
                # GRUP es alfanumérico corto
                if re.match(r'^[A-Z0-9]{2,4}$', part):
                    # Verificar que el siguiente sea un número (LOAD)
                    if i + 1 < len(parts) and parts[i + 1].replace('.', '').replace('-', '').replace('+', '').replace('E', '').isdigit():
                        grup_idx = i
                        break
            
            if grup_idx is None or grup_idx < 2:
                return None
            
            grup = parts[grup_idx]
            
            # MEMBER: todo entre JOINT y GRUP (CHD + BRC)
            member_parts = parts[1:grup_idx]
            member = ' '.join(member_parts)
            
            return {
                'joint': joint,
                'member': member,
                'grup': grup
            }
            
        except Exception as e:
            logger.debug(f"Línea {self.line_number}: No se pudo extraer identificadores: {e}")
            return None
    
    def _extract_damages(self, line: str) -> np.ndarray:
        """
        Extrae 8 valores de daño de línea *** TOTAL DAMAGE ***.
        
        Args:
            line: Línea con *** TOTAL DAMAGE ***
            
        Returns:
            np.ndarray de 8 valores float
            
        Raises:
            ValueError: Si no se pueden extraer 8 valores
        """
        # Dividir por ***
        parts = line.split('***')
        if len(parts) < 3:
            raise ValueError("Formato inválido de línea TOTAL DAMAGE")
        
        # Los valores están después del segundo ***
        values_str = parts[2].strip()
        values = values_str.split()
        
        if len(values) < 8:
            raise ValueError(f"Se esperaban 8 valores, se encontraron {len(values)}")
        
        # Convertir usando normalize_fortran_scientific
        damages = []
        for val_str in values[:8]:
            try:
                val_float = normalize_fortran_scientific(val_str)
                damages.append(val_float)
            except Exception as e:
                raise ValueError(f"Error convirtiendo '{val_str}': {e}")
        
        return np.array(damages, dtype=np.float64)


def parse_fatigue_file(filepath: str) -> ParseResult:
    """
    Función helper para parsear un archivo SACS FTG.
    
    Args:
        filepath: Ruta al archivo .txt de SACS
        
    Returns:
        ParseResult: Resultado del parsing
    """
    parser = FTGParser()
    return parser.parse_file(filepath)
