#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Virtual environment not activated"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Show available scripts
echo ""
echo "🤖 Available Bot Scripts:"
echo "1. smart_persistent_strategy.py - Bot dengan smart saving (RECOMMENDED)"
echo "2. persistent_strategy.py - Bot dengan data persistence"
echo "3. simple_strategy.py - Bot sederhana"
echo "4. scalping_strategy.py - Bot lengkap dengan AI"
echo "5. view_data.py - Lihat data historis"
echo "6. storage_analyzer.py - Analisis efisiensi storage"
echo ""

# Ask user which script to run
read -p "Pilih script (1-6): " choice

case $choice in
    1)
        echo "🚀 Running smart_persistent_strategy.py..."
        python smart_persistent_strategy.py
        ;;
    2)
        echo "🚀 Running persistent_strategy.py..."
        python persistent_strategy.py
        ;;
    3)
        echo "🚀 Running simple_strategy.py..."
        python simple_strategy.py
        ;;
    4)
        echo "🚀 Running scalping_strategy.py..."
        python scalping_strategy.py
        ;;
    5)
        echo "🔍 Running view_data.py..."
        python view_data.py
        ;;
    6)
        echo "📊 Running storage_analyzer.py..."
        python storage_analyzer.py
        ;;
    *)
        echo "❌ Pilihan tidak valid!"
        exit 1
        ;;
esac 