#!/usr/bin/env python3
"""
Script para generar output provisional de Etapa 1
Convierte notación Fortran a estándar en todo el archivo ftglstE1.txt
y guarda resultado en output_provisional/ftglstE1_etapa1.txt
"""

import sys
import os
import re

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaner import normalize_fortran_scientific, is_valid_data_line

def procesar_linea(line):
    """
    Procesa una línea reemplazando valores en notación Fortran.
    
    Args:
        line: Línea del archivo SACS
        
    Returns:
        Línea con valores normalizados
    """
    # Buscar todos los patrones de notación Fortran en la línea
    # Patrón: punto seguido de dígitos, signo, y dígitos (sin E)
    patron_fortran = r'(\.\d+[+-]\d+)'
    
    def reemplazar_valor(match):
        valor_original = match.group(1)
        try:
            # Intentar normalizar
            valor_float = normalize_fortran_scientific(valor_original)
            # Convertir de vuelta a string en notación estándar
            return f"{valor_float:.8E}"
        except:
            # Si falla, devolver original
            return valor_original
    
    # Reemplazar todos los valores Fortran en la línea
    linea_procesada = re.sub(patron_fortran, reemplazar_valor, line)
    return linea_procesada


def main():
    """Función principal."""
    
    # Rutas
    input_file = '../data/ftglstE1.txt'
    output_file = '../output_provisional/ftglstE1_etapa1.txt'
    
    # Obtener ruta absoluta desde la ubicación del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_file)
    output_path = os.path.join(script_dir, output_file)
    
    print("="*70)
    print("GENERACIÓN DE OUTPUT PROVISIONAL - ETAPA 1")
    print("="*70)
    print(f"\nArchivo entrada:  {input_path}")
    print(f"Archivo salida:   {output_path}")
    print("\nProcesando...")
    
    lineas_procesadas = 0
    valores_convertidos = 0
    
    try:
        with open(input_path, 'r', encoding='latin-1') as f_in:
            with open(output_path, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    # Contar valores Fortran en la línea original
                    patron = r'(\.\d+[+-]\d+)'
                    matches_antes = len(re.findall(patron, line))
                    
                    # Procesar línea
                    linea_procesada = procesar_linea(line)
                    
                    # Escribir al archivo de salida
                    f_out.write(linea_procesada)
                    
                    lineas_procesadas += 1
                    valores_convertidos += matches_antes
                    
                    # Progreso cada 10,000 líneas
                    if lineas_procesadas % 10000 == 0:
                        print(f"  Procesadas {lineas_procesadas:,} líneas...")
        
        print(f"\n✅ Proceso completado exitosamente!")
        print(f"\nEstadísticas:")
        print(f"  - Líneas procesadas:      {lineas_procesadas:,}")
        print(f"  - Valores convertidos:    {valores_convertidos:,}")
        print(f"\nArchivo generado: {output_path}")
        
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
