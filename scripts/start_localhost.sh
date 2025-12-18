#!/bin/bash

# Script para iniciar o ProdPlan 4.0 em localhost
# Backend: http://localhost:8000
# Frontend: http://localhost:5173

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/factory-optimizer/backend"
FRONTEND_DIR="$PROJECT_ROOT/factory-optimizer/frontend"

echo "🚀 Iniciando ProdPlan 4.0..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Erro: Diretórios backend ou frontend não encontrados!"
    exit 1
fi

# Função para iniciar backend
start_backend() {
    echo "📦 Iniciando Backend (porta 8000)..."
    cd "$BACKEND_DIR"
    
    # Verificar se existe venv
    if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
        echo "⚠️  Virtual environment não encontrado. Criando..."
        python3 -m venv .venv
    fi
    
    # Ativar venv
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Instalar dependências se necessário
    if ! python -c "import fastapi" 2>/dev/null; then
        echo "📥 Instalando dependências do backend..."
        pip install -q -r requirements.txt
    fi
    
    # Iniciar servidor
    echo "✅ Backend iniciando em http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    python run.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/prodplan_backend.pid
}

# Função para iniciar frontend
start_frontend() {
    echo ""
    echo "🎨 Iniciando Frontend CORRETO (factory-optimizer/frontend) na porta 5173..."
    cd "$FRONTEND_DIR"
    
    # Verificar se é o diretório correto
    if [ ! -f "src/App.tsx" ] || [ ! -d "src/pages/Prodplan.tsx" ]; then
        echo "❌ Erro: Este não é o frontend correto!"
        echo "   Esperado: factory-optimizer/frontend"
        exit 1
    fi
    
    # Verificar se node_modules existe
    if [ ! -d "node_modules" ]; then
        echo "📥 Instalando dependências do frontend..."
        npm install
    fi
    
    # Iniciar servidor de desenvolvimento
    echo "✅ Frontend CORRETO iniciando em http://localhost:5173"
    echo "   (Com todas as funcionalidades: ProdPlan, SmartInventory, Duplios, Digital Twin, etc.)"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/prodplan_frontend.pid
}

# Função para parar servidores
stop_servers() {
    echo ""
    echo "🛑 Parando servidores..."
    if [ -f /tmp/prodplan_backend.pid ]; then
        kill $(cat /tmp/prodplan_backend.pid) 2>/dev/null || true
        rm /tmp/prodplan_backend.pid
    fi
    if [ -f /tmp/prodplan_frontend.pid ]; then
        kill $(cat /tmp/prodplan_frontend.pid) 2>/dev/null || true
        rm /tmp/prodplan_frontend.pid
    fi
    # Matar processos uvicorn e vite que possam estar rodando
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    echo "✅ Servidores parados"
}

# Trap para parar servidores ao sair
trap stop_servers EXIT INT TERM

# Iniciar servidores
start_backend
sleep 2
start_frontend

echo ""
echo "✨ ProdPlan 4.0 está rodando!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Pressione Ctrl+C para parar os servidores"
echo ""

# Manter script rodando
wait

