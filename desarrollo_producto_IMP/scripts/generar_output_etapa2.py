#!/usr/bin/env python3
"""
Script para generar output provisional de Etapa 2
Parsea archivos SACS FTG y extrae elementos estructurados
Guarda resultado en output_provisional/ftglstE1_etapa2.csv
"""

import sys
import os
import pandas as pd

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ftg_parser import parse_fatigue_file


def main():
    """Función principal."""
    
    # Rutas
    input_file = '../data/ftglstE1.txt'
    output_file = '../output_provisional/ftglstE1_etapa2.csv'
    
    # Obtener ruta absoluta desde la ubicación del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_file)
    output_path = os.path.join(script_dir, output_file)
    
    print("="*70)
    print("GENERACIÓN DE OUTPUT PROVISIONAL - ETAPA 2")
    print("="*70)
    print(f"\nArchivo entrada:  {input_path}")
    print(f"Archivo salida:   {output_path}")
    print("\nParseando archivo...")
    
    try:
        # Parsear archivo
        result = parse_fatigue_file(input_path)
        
        print(f"\n✅ Parsing completado!")
        print(f"\nEstadísticas:")
        print(f"  - Elementos extraídos:    {result.total_elements:,}")
        print(f"  - Errores:                {len(result.errors)}")
        print(f"  - Advertencias:           {len(result.warnings)}")
        
        if result.total_elements == 0:
            print("\n⚠️  No se extrajeron elementos. Verificar formato del archivo.")
            sys.exit(1)
        
        # Convertir a DataFrame
        print("\nGenerando DataFrame...")
        data = []
        for element in result.elements.values():
            data.append(element.to_dict())
        
        df = pd.DataFrame(data)
        
        # Ordenar por daño máximo (descendente)
        df = df.sort_values('MAX_DAMAGE', ascending=False)
        
        # Guardar a CSV
        df.to_csv(output_path, index=False)
        
        print(f"\n✅ Archivo CSV generado: {output_path}")
        
        # Mostrar resumen
        summary = result.get_summary()
        print(f"\n📊 Resumen:")
        print(f"  - Daño máximo:           {summary['max_damage_overall']:.6e}")
        print(f"  - Elemento crítico:      {summary.get('critical_element', 'N/A')}")
        print(f"  - Ubicación crítica:     {summary.get('critical_location', 'N/A')}")
        
        # Mostrar top 10 elementos
        print(f"\n🔝 Top 10 elementos con mayor daño:")
        print(df[['JOINT', 'MEMBER', 'GRUP', 'MAX_DAMAGE', 'CRITICAL_LOCATION']].head(10).to_string(index=False))
        
        # Si hay errores, mostrarlos
        if result.errors:
            print(f"\n⚠️  Errores encontrados:")
            for error in result.errors[:5]:  # Mostrar primeros 5
                print(f"  - {error}")
        
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
