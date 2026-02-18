"""
Test Suite para Módulo de Limpieza y Normalización de Datos SACS
Etapa 1: Procesador de Fatiga SACS v1.0

Tests para las funciones de normalización Fortran, detección de encoding
y filtrado de líneas.
"""

import pytest
import os
import sys

# Agregar src/ al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaner import (
    normalize_fortran_scientific,
    detect_file_encoding,
    is_valid_data_line
)


class TestNormalizeFortranScientific:
    """Tests para la función normalize_fortran_scientific()"""
    
    def test_fortran_negative_exponent_decimal(self):
        """Caso: .dígitos-exponente (sin 0 inicial)"""
        result = normalize_fortran_scientific('.48430268-9')
        expected = 0.48430268e-9
        assert abs(result - expected) < 1e-15, f"Expected {expected}, got {result}"
    
    def test_fortran_negative_exponent_decimal_2(self):
        """Otro caso de notación Fortran básica"""
        result = normalize_fortran_scientific('.10756032-8')
        expected = 0.10756032e-8
        assert abs(result - expected) < 1e-15
    
    def test_fortran_positive_exponent(self):
        """Caso: exponente positivo"""
        result = normalize_fortran_scientific('.123+4')
        expected = 0.123e+4
        assert abs(result - expected) < 1e-10
    
    def test_standard_scientific_notation(self):
        """Caso: notación estándar ya correcta (con E)"""
        result = normalize_fortran_scientific('0.817300E-05')
        expected = 0.817300e-5
        assert abs(result - expected) < 1e-15
    
    def test_fortran_without_leading_zero(self):
        """Caso: número sin 0 inicial como 1.23-4"""
        result = normalize_fortran_scientific('1.23-4')
        expected = 1.23e-4
        assert abs(result - expected) < 1e-15
    
    def test_integer_with_exponent(self):
        """Caso: número entero con exponente 123-4"""
        result = normalize_fortran_scientific('123-4')
        expected = 123e-4
        assert abs(result - expected) < 1e-15
    
    def test_large_number(self):
        """Caso: número grande con exponente positivo"""
        result = normalize_fortran_scientific('5.67+8')
        expected = 5.67e+8
        assert abs(result - expected) < 1e5
    
    def test_very_small_number(self):
        """Caso: número muy pequeño (típico en fatiga)"""
        result = normalize_fortran_scientific('.3260751-10')
        expected = 0.3260751e-10
        assert abs(result - expected) < 1e-20
    
    def test_whitespace_handling(self):
        """Caso: string con espacios al inicio/final"""
        result = normalize_fortran_scientific('  .123-4  ')
        expected = 0.123e-4
        assert abs(result - expected) < 1e-15
    
    def test_invalid_format_raises_error(self):
        """Caso: formato inválido debe lanzar ValueError"""
        with pytest.raises(ValueError):
            normalize_fortran_scientific('invalid')
    
    def test_empty_string_raises_error(self):
        """Caso: string vacío debe lanzar ValueError"""
        with pytest.raises(ValueError):
            normalize_fortran_scientific('')
    
    def test_empty_whitespace_raises_error(self):
        """Caso: solo espacios debe lanzar ValueError"""
        with pytest.raises(ValueError):
            normalize_fortran_scientific('   ')
    
    def test_wrong_type_raises_error(self):
        """Caso: tipo incorrecto debe lanzar TypeError"""
        with pytest.raises(TypeError):
            normalize_fortran_scientific(123)
    
    def test_none_type_raises_error(self):
        """Caso: None debe lanzar TypeError"""
        with pytest.raises(TypeError):
            normalize_fortran_scientific(None)


class TestDetectFileEncoding:
    """Tests para la función detect_file_encoding()"""
    
    def test_detect_existing_file(self):
        """Caso: archivo real del proyecto (ftglstE1.txt)"""
        filepath = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'ftglstE1.txt'
        )
        
        if os.path.exists(filepath):
            encoding = detect_file_encoding(filepath)
            # Debe retornar un encoding válido
            assert encoding in ['utf-8', 'latin-1', 'windows-1252', 'ascii', 'ISO-8859-1']
        else:
            pytest.skip("Archivo ftglstE1.txt no encontrado")
    
    def test_nonexistent_file_raises_error(self):
        """Caso: archivo inexistente debe lanzar FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            detect_file_encoding('/path/que/no/existe/archivo.txt')


class TestIsValidDataLine:
    """Tests para la función is_valid_data_line()"""
    
    def test_empty_line_invalid(self):
        """Caso: línea vacía debe ser filtrada"""
        assert is_valid_data_line('') is False
    
    def test_whitespace_only_invalid(self):
        """Caso: solo espacios debe ser filtrada"""
        assert is_valid_data_line('     ') is False
    
    def test_sacs_header_invalid(self):
        """Caso: encabezado SACS debe ser filtrado"""
        line = 'SACS (2024)                         FTG PAGE  810'
        assert is_valid_data_line(line) is False
    
    def test_page_number_invalid(self):
        """Caso: número de página debe ser filtrado"""
        line = '   PLATAFORMA DE PERFORACION KU-F           FTG PAGE  1640'
        assert is_valid_data_line(line) is False
    
    def test_separator_line_invalid(self):
        """Caso: línea de separación debe ser filtrada"""
        assert is_valid_data_line('-------------------------------------------') is False
    
    def test_company_line_invalid(self):
        """Caso: línea con info de empresa debe ser filtrada"""
        line = '                                            Company: Company'
        assert is_valid_data_line(line) is False
    
    def test_date_line_invalid(self):
        """Caso: línea con fecha debe ser filtrada"""
        line = '           DATE 01-OCT-2025  TIME 16:05:07   FTG PAGE    1'
        assert is_valid_data_line(line) is False
    
    def test_column_header_invalid(self):
        """Caso: encabezado de columnas debe ser filtrado"""
        line = 'JOINT   MEMBER  GRUP FATG     TOP       TOP-LEFT      LEFT'
        assert is_valid_data_line(line) is False
    
    def test_total_damage_valid(self):
        """Caso IMPORTANTE: *** TOTAL DAMAGE *** debe ser VÁLIDO"""
        line = '   *** TOTAL DAMAGE ***   0.817E-05 0.727E-05 0.445E-05'
        assert is_valid_data_line(line) is True
    
    def test_data_line_valid(self):
        """Caso: línea de datos debe ser válida"""
        line = '0003  802L 0005  16A   1  .48430268-9 .30372732-9'
        assert is_valid_data_line(line) is True
    
    def test_continuation_line_valid(self):
        """Caso: línea de continuación con datos debe ser válida"""
        line = '                       2  .72777048-9 .73980208-9'
        assert is_valid_data_line(line) is True
    
    def test_member_with_space_valid(self):
        """Caso: línea con MEMBER conteniendo espacio"""
        line = '0002  0002-501L  52A   1  .48430268-9 .30372732-9'
        assert is_valid_data_line(line) is True
    
    def test_section_header_invalid(self):
        """Caso: encabezados de sección genéricos deben ser filtrados"""
        line = '   *** GENERAL OPTIONS ***'
        assert is_valid_data_line(line) is False


class TestIntegration:
    """Tests de integración con datos reales"""
    
    def test_normalize_multiple_fortran_values(self):
        """Caso: normalizar múltiples valores de una línea real"""
        # Valores extraídos de línea típica de ftglstE1.txt
        values = ['.48430268-9', '.30372732-9', '.60312636-9', '.10756032-8']
        
        results = [normalize_fortran_scientific(v) for v in values]
        
        # Verificar que todos son floats válidos
        assert all(isinstance(r, float) for r in results)
        
        # Verificar que todos son valores pequeños positivos (típico de fatiga)
        assert all(0 < r < 1e-6 for r in results)
    
    def test_filter_page_header_block(self):
        """Caso: filtrar bloque completo de encabezado de página"""
        lines = [
            ' SACS (2024)                                                  Company: Company',
            '   PLATAFORMA DE PERFORACION KU-F           DATE 01-OCT-2025  TIME 16:05:07   FTG PAGE    1',
            '',
            '                    * *  M E M B E R  F A T I G U E  D E T A I L  R E P O R T  * *',
            '',
            'JOINT   MEMBER  GRUP FATG     TOP       TOP-LEFT      LEFT',
        ]
        
        valid_lines = [line for line in lines if is_valid_data_line(line)]
        
        # Ninguna línea del encabezado debe pasar el filtro
        assert len(valid_lines) == 0


if __name__ == '__main__':
    # Ejecutar tests con pytest
    pytest.main([__file__, '-v'])
