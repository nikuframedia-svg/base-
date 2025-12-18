# 🔴 Gaps de Implementação Frontend - ProdPlan 4.0

## Análise Detalhada por Módulo

---

## 1. 🏭 PRODPLAN / PLANNING

### Endpoints Backend Disponíveis:
```
GET  /api/planning/v2/plano        → Obter plano atual
POST /api/planning/v2/recalculate  → Recalcular plano
GET  /api/planning/v2/config       → Obter configuração
POST /api/planning/v2/config       → Atualizar configuração
GET  /api/planning/v2/diagnose-routes → Diagnóstico
POST /api/planning/v2/audit-routes    → Auditoria
POST /api/planning/chat/interpret     → Interpretar comando NL
POST /api/planning/chat/apply         → Aplicar comando
```

### O que existe no Frontend:
- ✅ `Planning.tsx` - Página principal com Gantt
- ✅ `AdvancedPlanning.tsx` - Configuração avançada
- ✅ `UnifiedGantt.tsx` - Componente Gantt
- 🟡 Chat de planeamento integrado

### O que FALTA:
1. **Gantt Interativo Completo**
   - ⬜ Drag & drop de operações
   - ⬜ Tooltip com detalhes da operação
   - ⬜ Zoom temporal (hora/dia/semana)
   - ⬜ Filtro por máquina/artigo/rota

2. **Chat de Planeamento Melhorado**
   - ⬜ UI para comandos rápidos (botões)
   - ⬜ Feedback visual de comando aplicado
   - ⬜ Histórico de comandos
   - ⬜ Auto-complete de máquinas/artigos

3. **Configuração APS**
   - ⬜ UI para pesos de objetivo
   - ⬜ UI para preferências de rota
   - ⬜ UI para configurar overlap

---

## 2. 🔥 BOTTLENECKS

### Endpoints Backend Disponíveis:
```
GET /api/bottlenecks/?demo=false
```

### Dados que o Backend Retorna:
```json
{
  "bottlenecks": [{
    "recurso": "M-27",
    "utilizacao_pct": 92.5,
    "fila_horas": 40.0,
    "probabilidade": 0.95,
    "drivers": ["Alta utilização", "Fila acumulada"],
    "acao": "Mover para Alternativa",
    "impacto_otd": 4.75,
    "impacto_horas": 4.0
  }],
  "top_losses": [...],
  "heatmap": [{
    "recurso": "M-27",
    "utilizacao": [
      {"hora": 0, "utilizacao_pct": 92.0},
      {"hora": 8, "utilizacao_pct": 95.0},
      ...
    ]
  }],
  "overlap_applied": {
    "transformacao": 0.15,
    "acabamentos": 0.20,
    "embalagem": 0.10
  },
  "lead_time_gain": 12.5
}
```

### O que existe no Frontend:
- ✅ `Bottlenecks.tsx` - Página básica
- ✅ `Heatmap.tsx` - Componente (duplicado?)
- ✅ `KPICard.tsx` - Cards de KPIs

### O que FALTA:
1. **Heatmap Real**
   - ⬜ Renderizar dados do backend (não mock)
   - ⬜ Cores por nível de utilização
   - ⬜ Tooltip com detalhes
   - ⬜ Eixo temporal dinâmico

2. **Cards de Gargalos**
   - ⬜ Lista ordenada por probabilidade
   - ⬜ Botão "Aplicar Ação"
   - ⬜ Indicador visual de prioridade

3. **Drill-down**
   - ⬜ Clicar em gargalo → ver detalhes
   - ⬜ Ver operações afetadas
   - ⬜ Ver alternativas

---

## 3. 📦 SMART INVENTORY

### Endpoints Backend Disponíveis:
```
GET /api/inventory/?classe=A&search=SKU&recalculate_rop=false
GET /api/inventory/rop?sku=SKU-001&service_level=0.95
```

### Dados que o Backend Retorna:
```json
{
  "matrix": {
    "A": {"X": 12, "Y": 8, "Z": 3},
    "B": {"X": 15, "Y": 12, "Z": 6},
    "C": {"X": 25, "Y": 35, "Z": 40}
  },
  "skus": [{
    "sku": "SKU-001",
    "classe": "A",
    "xyz": "X",
    "stock_atual": 120,
    "ads_180": 24.5,
    "cobertura_dias": 5,
    "risco_30d": 95.0,
    "rop": 200,
    "acao": "Repor urgente"
  }],
  "kpis": {...},
  "top_risks": [...],
  "generated_at": "2024-12-17T10:00:00"
}
```

### O que existe no Frontend:
- ✅ `SmartInventory.tsx` - Página principal
- ✅ `SmartInventory/index.tsx` - Router
- ✅ `SmartInventoryOverview.tsx` - Overview
- ✅ `SmartInventoryWIP.tsx` - WIP Flow

### O que FALTA:
1. **Matriz ABC/XYZ Interativa**
   - ⬜ Grid 3x3 clicável
   - ⬜ Cores por criticidade
   - ⬜ Filtrar SKUs por célula
   - ⬜ Contagem em cada célula

2. **Tabela de SKUs**
   - ⬜ Ordenação por coluna
   - ⬜ Filtros avançados
   - ⬜ Ações inline (recalcular ROP)
   - ⬜ Export CSV

3. **Detalhes de SKU**
   - ⬜ Modal com gráfico de cobertura
   - ⬜ Histórico de movimentos
   - ⬜ Previsão Monte Carlo

---

## 4. 💬 CHAT

### Endpoints Backend Disponíveis:
```
POST /api/chat/
  Request: { messages, mode, temperature }
  Response: { answer, model, used_context, mode }
```

### O que existe no Frontend:
- ✅ `Chat.tsx` - Página de chat

### O que FALTA:
1. **UI Melhorada**
   - ⬜ Markdown rendering melhor
   - ⬜ Syntax highlighting para código
   - ⬜ Tabelas formatadas
   - ⬜ Loading state com skeleton

2. **Funcionalidades**
   - ⬜ Histórico persistente
   - ⬜ Modo selection (dropdown)
   - ⬜ Copiar resposta
   - ⬜ Exportar conversa

---

## 5. 💡 SUGGESTIONS

### Endpoints Backend Disponíveis:
```
GET /api/suggestions/?mode=planeamento|gargalos|inventario|resumo
```

### Dados que o Backend Retorna:
```json
{
  "count": 5,
  "items": [{
    "id": "suggestion-1",
    "icon": "⚙️",
    "action": "Desviar 30% de carga de M-27 para M-29",
    "explanation": "Prioridade: ALTO | Utilização: 92.5%",
    "impact": "Lead time: -8h, OTD: +2.5pp",
    "impact_level": "alto",
    "reasoning_markdown": "**Porquê esta sugestão?** ...",
    "dados_base": {...},
    "impacto_estimado": {...},
    "prioridade": "ALTO"
  }],
  "mode": "planeamento"
}
```

### O que existe no Frontend:
- ✅ `Suggestions.tsx` - Página básica

### O que FALTA:
1. **Cards de Sugestão**
   - ⬜ Expandir para ver reasoning
   - ⬜ Botão "Aplicar" funcional
   - ⬜ Indicador de impacto visual
   - ⬜ Filtro por tipo/prioridade

2. **Ações**
   - ⬜ Integrar com Planning Chat
   - ⬜ Confirmação antes de aplicar
   - ⬜ Feedback de sucesso/erro

---

## 6. 🔮 WHAT-IF

### Endpoints Backend Disponíveis:
```
POST /api/whatif/vip
  Request: { sku, quantidade, prazo }
  
POST /api/whatif/avaria
  Request: { recurso, de, ate }
```

### O que existe no Frontend:
- ✅ `WhatIf.tsx` - Página básica
- ✅ `ZDMSimulator.tsx` - Simulador ZDM

### O que FALTA:
1. **UI de Simulação VIP**
   - ⬜ Autocomplete de SKUs
   - ⬜ Date picker para prazo
   - ⬜ Validação de inputs

2. **UI de Simulação Avaria**
   - ⬜ Autocomplete de recursos
   - ⬜ Range picker para período
   - ⬜ Preview de operações afetadas

3. **Resultados**
   - ⬜ Comparativo antes/depois
   - ⬜ Gráfico de impacto
   - ⬜ Lista de operações reordenadas

---

## 7. 📤 ETL

### Endpoints Backend Disponíveis:
```
POST /api/etl/upload   → Upload de ficheiros
GET  /api/etl/preview  → Preview de dados
POST /api/etl/mapping  → Configurar mapeamento
GET  /api/etl/status   → Status do ETL
```

### O que existe no Frontend:
- ✅ `ETLPage.tsx` - Página básica

### O que FALTA:
1. **Upload**
   - ⬜ Drag & drop zone
   - ⬜ Progress bar
   - ⬜ Validação de formato

2. **Preview**
   - ⬜ Tabela com dados
   - ⬜ Mapeamento de colunas
   - ⬜ Confirmar/rejeitar mapeamento

3. **Status**
   - ⬜ Timeline de processamento
   - ⬜ Erros detalhados
   - ⬜ Histórico de uploads

---

## 8. 🔧 TECHNICAL QUERIES

### Endpoints Backend Disponíveis:
```
GET /api/technical/alternatives?artigo=X&rota=Y&operacao=Z
GET /api/technical/routes?artigo=X
GET /api/technical/operations?machine_id=X
GET /api/technical/families?machine_id=X
GET /api/technical/validate?entity_type=machine&machine_id=X
```

### O que existe no Frontend:
- ✅ `TechnicalQueriesPage.tsx` - Página básica

### O que FALTA:
1. **Interface de Consulta**
   - ⬜ Autocomplete de entidades
   - ⬜ Resultados em tabela
   - ⬜ Validação em tempo real

2. **Visualização**
   - ⬜ Grafo de alternativas
   - ⬜ Diagrama de rotas
   - ⬜ Árvore de operações

---

## 9. 📊 DASHBOARDS (Compatibilidade)

### Endpoints Backend Disponíveis (STUBS):
```
GET /dashboards/utilization-heatmap
GET /dashboards/operator
GET /dashboards/machine-oee
GET /dashboards/cell-performance
GET /dashboards/capacity-projection
```

**NOTA**: Estes endpoints são STUBS que retornam dados vazios.
Precisam de implementação real no backend primeiro.

### O que existe no Frontend:
- ✅ `Dashboards.tsx` - Página genérica
- ✅ `ProdplanDashboards.tsx` - Dashboard Prodplan

### O que FALTA:
1. **Backend** (prioridade)
   - ⬜ Implementar lógica real nos endpoints
   - ⬜ Calcular OEE a partir de dados
   - ⬜ Projeção de capacidade

2. **Frontend**
   - ⬜ Charts com Recharts
   - ⬜ Filtros de período
   - ⬜ Export de dados

---

## 🎯 PRIORIDADES DE IMPLEMENTAÇÃO

### Sprint 1 - Core Features
1. ⬜ **Planning Gantt** - Interatividade básica
2. ⬜ **Bottlenecks Heatmap** - Dados reais
3. ⬜ **Inventory Matrix** - Grid interativo
4. ⬜ **Suggestions Actions** - Botões funcionais

### Sprint 2 - Chat & Commands
5. ⬜ **Planning Chat UI** - Comandos rápidos
6. ⬜ **Chat History** - Persistência
7. ⬜ **What-If Complete** - Formulários e resultados

### Sprint 3 - Data Management
8. ⬜ **ETL Full Flow** - Upload + preview + mapping
9. ⬜ **Technical Queries UI** - Consultas completas
10. ⬜ **Dashboards** - Implementar backend + UI

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Componentes UI Necessários
- [ ] `MatrixGrid` - Grid 3x3 para ABC/XYZ
- [ ] `HeatmapChart` - Mapa de calor real
- [ ] `GanttInteractive` - Gantt com drag & drop
- [ ] `CommandPalette` - Comandos rápidos
- [ ] `AutocompleteInput` - Input com sugestões
- [ ] `DateRangePicker` - Seletor de período
- [ ] `ComparisonChart` - Gráfico antes/depois
- [ ] `DrilldownTable` - Tabela com expansão

### Hooks Necessários
- [ ] `useWIPFlow` - Hook para WIP data
- [ ] `usePlanningCommands` - Hook para comandos
- [ ] `useSimulation` - Hook para what-if
- [ ] `useBottlenecks` - Hook para gargalos

### Services a Melhorar
- [ ] `apiService` - Já existe, manter atualizado
- [ ] `websocket` - Para updates em tempo real (futuro)

---

*Documento gerado em: 2024-12-17*




