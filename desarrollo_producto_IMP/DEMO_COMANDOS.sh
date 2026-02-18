#!/bin/bash
# Script de Demo para Reunión Etapa 1
# Ejecutar: bash DEMO_COMANDOS.sh

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         DEMO ETAPA 1 - PROCESADOR DE FATIGA SACS v1.0           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Ir al directorio del proyecto
cd /home/fcisnerosr/github/desarrollo_producto_IMP

echo "📍 Ubicación: $(pwd)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  EJECUTAR TESTS (3 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Comando:"
echo "  conda run -n procesador_fatiga_sacs pytest tests/test_data_cleaner.py -v"
echo ""
read -p "Presiona ENTER para ejecutar tests..."

conda run -n procesador_fatiga_sacs pytest tests/test_data_cleaner.py -v

echo ""
echo "✅ Tests completados"
echo ""
read -p "Presiona ENTER para continuar..."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  VER COBERTURA DE CÓDIGO (opcional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Comando:"
echo "  conda run -n procesador_fatiga_sacs pytest tests/test_data_cleaner.py --cov=src --cov-report=term"
echo ""
read -p "¿Ejecutar reporte de cobertura? (s/n): " respuesta

if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    conda run -n procesador_fatiga_sacs pytest tests/test_data_cleaner.py --cov=src --cov-report=term
    echo ""
    echo "📊 Reporte HTML disponible en: htmlcov/index.html"
fi

echo ""
read -p "Presiona ENTER para continuar..."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  ABRIR NOTEBOOK DEMO (Jupyter)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Comando:"
echo "  conda run -n procesador_fatiga_sacs jupyter notebook notebooks/demo_etapa1.ipynb"
echo ""
echo "⚠️  NOTA: Esto abrirá el navegador. Ejecutar celdas en orden durante la demo."
echo ""
read -p "¿Abrir Jupyter Notebook? (s/n): " respuesta

if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    echo ""
    echo "🚀 Abriendo Jupyter Notebook..."
    conda run -n procesador_fatiga_sacs jupyter notebook notebooks/demo_etapa1.ipynb
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  ARCHIVOS CLAVE PARA MOSTRAR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Abrir en VS Code o editor:"
echo "  📄 PRESENTACION_ETAPA1.md      (resumen ejecutivo)"
echo "  📄 GUIA_REUNION.md             (script de la junta)"
echo "  📄 src/data_cleaner.py         (código fuente)"
echo "  📄 tests/test_data_cleaner.py  (tests)"
echo "  📊 htmlcov/index.html          (cobertura HTML)"
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEMO LISTA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Resumen de logros para mencionar:"
echo "  • 3 funciones implementadas"
echo "  • 31 tests (100% pasan)"
echo "  • 72% cobertura de código"
echo "  • Validado con 146,370 líneas de datos reales"
echo "  • Tiempo: 0.07s para todos los tests"
echo ""
echo "💡 Próximos pasos: Etapa 2 (Parser con máquina de estados)"
echo ""
