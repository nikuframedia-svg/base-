# 🌐 Localhost - ProdPlan 4.0

## ✅ Frontend CORRETO está a funcionar!

**URL:** http://localhost:5173

**Diretório:** `factory-optimizer/frontend/` (NÃO o `frontend/` antigo)

### 📋 Funcionalidades Disponíveis

O frontend correto inclui **32 páginas** com todas as funcionalidades:

#### Módulos Principais:
- ✅ **ProdPlan** - Planeamento completo (Gantt, Dashboards, Gargalos, Máquinas, etc.)
- ✅ **SmartInventory** - Inventário inteligente (MRP, Forecast, ROP, etc.)
- ✅ **Duplios** - Passaportes Digitais (PDM, DPP, Compliance, Trust Index)
- ✅ **Digital Twin** - Gêmeos Digitais (Máquinas SHI-DT, Produto XAI-DT)
- ✅ **Inteligência** - IA & Otimização (Causal, MILP, What-If)
- ✅ **R&D** - Investigação (WP1-WP4, WPX)
- ✅ **Chat** - Copilot industrial

### 🔧 Backend

**URL:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 🚀 Como Iniciar

```bash
# Opção 1: Tudo de uma vez
./scripts/start_localhost.sh

# Opção 2: Separadamente
./scripts/start_backend.sh    # Terminal 1
./scripts/start_frontend.sh    # Terminal 2
```

### ⚠️ Nota Importante

O diretório `frontend/` na raiz é o **frontend antigo** (6 páginas apenas) e **NÃO está a ser usado**.

O frontend correto está em `factory-optimizer/frontend/` (32 páginas com todas as funcionalidades).

### 🧹 Limpeza

Se quiser remover o frontend antigo do disco (opcional):

```bash
# ATENÇÃO: Isto remove o diretório fisicamente
rm -rf frontend/
```

Mas não é necessário - o servidor já está a usar o correto!


