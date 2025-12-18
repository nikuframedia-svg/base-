#!/bin/bash

# Script para iniciar apenas o frontend CORRETO (factory-optimizer/frontend)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/factory-optimizer/frontend"

echo "🎨 Iniciando Frontend CORRETO (factory-optimizer/frontend)"
echo "📁 Diretório: $FRONTEND_DIR"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Erro: Diretório frontend não encontrado em $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# Verificar dependências
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependências..."
    npm install
fi

echo "✅ Frontend iniciando em http://localhost:5173"
echo "   (Frontend correto com todas as funcionalidades: ProdPlan, SmartInventory, Duplios, Digital Twin, etc.)"
npm run dev

