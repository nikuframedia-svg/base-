#!/bin/bash

# Script para iniciar apenas o backend
cd "$(dirname "${BASH_SOURCE[0]}")/../factory-optimizer/backend"

# Ativar venv se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Verificar dependências
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Instalando dependências..."
    pip install -r requirements.txt
fi

echo "🚀 Iniciando Backend em http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
python run.py




