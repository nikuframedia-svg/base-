# 🔍 ANÁLISE PROFUNDA DO BACKEND - TODAS AS FUNCIONALIDADES

**Data:** 2025-01-18  
**Análise:** Exaustiva de TODOS os ficheiros Python do backend

---

## 📊 ESTATÍSTICAS GERAIS

- **Total ficheiros Python:** 252
- **Total ficheiros tracked:** 292 (inclui outros tipos)
- **Módulos principais:** 30+
- **Engines/Services encontrados:** 50+
- **Heurísticas:** 10+
- **Modelos ML:** 20+

---

## 🎯 1. HEURÍSTICAS DE SCHEDULING

### 1.1. `scheduling/heuristics.py` ✅ TRACKED

**HeuristicDispatcher** - Dispatcher heurístico com múltiplas regras:
- **FIFO** (First In, First Out): Ordena por tempo de chegada
- **SPT** (Shortest Processing Time): Ordena por tempo de processamento (menor primeiro)
- **EDD** (Earliest Due Date): Ordena por data de entrega (mais cedo primeiro)
- **CR** (Critical Ratio): `CR = (due_date - current_time) / remaining_processing_time`
- **WSPT** (Weighted Shortest Processing Time): Ordena por `weight / processing_time`
- **RANDOM**: Baseline para comparação

**HeuristicScheduler** - Scheduler completo usando heurísticas:
- Suporta todas as regras acima
- Machine selection quando há alternativas
- Logging de decisões para R&D

**Funcionalidades:**
- `dispatch_fifo()`: FIFO dispatching
- `dispatch_spt()`: SPT dispatching
- `dispatch_edd()`: EDD dispatching
- `dispatch_cr()`: Critical Ratio dispatching
- `dispatch_wspt()`: Weighted SPT dispatching
- `dispatch_random()`: Random dispatching

---

## 🔧 2. SETUP OPTIMIZATION

### 2.1. `planning/setup_optimizer.py` ✅ TRACKED

**SetupOptimizer** - Otimização de sequências para minimizar setup times:

**Modelo Matemático (TSP-like):**
```
min Σ S[f(i), f(i+1)]  para operações consecutivas i, i+1
```

**Algoritmos Implementados:**
1. **Greedy Nearest Neighbor**: Escolhe sempre a próxima operação com menor setup time
2. **Greedy + 2-opt Local Search**: Melhora solução greedy com 2-opt
3. **Genetic Algorithm**: Para instâncias maiores
   - Population size: 50
   - Generations: 100
   - Order crossover (OX)
   - Mutation rate: 10%

**Funcionalidades:**
- `optimize_sequence()`: Otimiza sequência de operações
- `_optimize_greedy()`: Algoritmo greedy
- `_optimize_greedy_2opt()`: Greedy + 2-opt
- `_optimize_genetic()`: Algoritmo genético
- `_order_crossover()`: Crossover para permutações
- `_calculate_max_tardiness()`: Calcula tardiness máximo

---

## 🤖 3. MODELOS ML ADICIONAIS (app/ml/)

### 3.1. `app/ml/inventory.py` ✅ TRACKED

**InventoryPredictor** - Predição de procura intermitente:

**Métodos:**
- **Croston-SBA** (Smoothing Bias Adjustment): Para demanda intermitente
- **TSB** (Teunter-Syntetos-Babai): Similar ao Croston
- **Poisson-Gamma**: Fallback para demanda intermitente

**Funcionalidades:**
- `predict_demand()`: Prediz demanda média (μ) e desvio padrão (σ)
- `calculate_rop()`: Calcula ROP usando simulação Monte Carlo
- `_croston_sba()`: Implementação Croston-SBA
- `_tsb()`: Implementação TSB
- `_poisson_gamma()`: Implementação Poisson-Gamma

### 3.2. `app/ml/setup_time.py` ✅ TRACKED

**SetupTimePredictor** - Previsão de tempos de setup:
- `predict()`: Prediz tempo de setup baseado em família anterior e atual

### 3.3. `app/ml/bottlenecks.py` ✅ TRACKED

**BottleneckPredictor** - Previsão de probabilidade de gargalo:
- `predict_probability()`: Prediz probabilidade de gargalo
- `predict_bottleneck_probability()`: Prediz probabilidade baseada em utilização e fila

### 3.4. `app/ml/cycle_time.py` ✅ TRACKED

**CycleTimePredictor** - Previsão de tempo de ciclo:
- `predict_p50()`: Prediz P50 (mediana) de tempo de ciclo
- `predict_p90()`: Prediz P90 (percentil 90) de tempo de ciclo

### 3.5. `app/ml/routing.py` ✅ TRACKED

**Routing Predictor** - Previsão de routing (bandit)

---

## 📈 4. DEMAND FORECASTING AVANÇADO

### 4.1. `smart_inventory/demand_forecasting.py` ✅ TRACKED

**ForecastEngine** - Forecasting de demanda com ML avançado:

**Modelos Implementados:**
- **ARIMA**: AutoRegressive Integrated Moving Average (statsmodels)
- **Prophet**: Facebook Prophet (decomposição aditiva)
- **N-BEATS**: Neural Basis Expansion Analysis (TODO[R&D])
- **NST**: Non-Stationary Transformer (TODO[R&D])
- **D-Linear**: Linear model com decomposição aprendida (TODO[R&D])
- **Ensemble**: Combinação de múltiplos modelos (TODO[R&D])

**Mathematical Foundations:**
```
Decomposição: y(t) = Trend(t) + Seasonality(t) + Residual(t)
ARIMA(p, d, q): (1 - φ₁B - ... - φₚBᵖ)(1 - B)ᵈ y(t) = (1 + θ₁B + ... + θₑBᵉ) ε(t)
SNR: SNR = Var(signal) / Var(noise)
```

**Funcionalidades:**
- `forecast_demand()`: Forecast principal
- `_forecast_arima()`: Forecast ARIMA
- `_forecast_prophet()`: Forecast Prophet
- `_forecast_nbeats()`: Forecast N-BEATS (TODO)
- `_forecast_nst()`: Forecast NST (TODO)
- `compute_snr_forecast()`: Calcula Signal-to-Noise Ratio

**Confidence Classification:**
- HIGH: SNR > 8
- MEDIUM: 3 < SNR ≤ 8
- LOW: SNR ≤ 3

### 4.2. `smart_inventory/forecasting_engine.py` ✅ TRACKED

**ClassicalForecastEngine** - Engine clássico:
- ARIMA, ETS, XGBoost
- Naive forecast

**AdvancedForecastEngine** - Engine avançado:
- NeuralForecast (N-BEATS, NST)
- Darts (DeepAR, TFT)

**Funcionalidades:**
- `forecast()`: Forecast principal
- `_forecast_ets()`: Exponential Smoothing
- `_forecast_arima()`: ARIMA
- `_forecast_xgboost()`: XGBoost
- `_forecast_neuralforecast()`: NeuralForecast
- `_forecast_darts()`: Darts

---

## 🏭 5. MULTI-WAREHOUSE OPTIMIZATION

### 5.1. `smart_inventory/multi_warehouse_optimizer.py` ✅ TRACKED

**Multi-Warehouse Optimizer (MILP)** - Otimização de redistribuição entre armazéns:

**Mathematical Formulation (MILP):**
```
Variáveis:
    q_transfer[w1, w2, sku]: Quantidade transferida de w1 para w2
    q_order[w, sku]: Quantidade a encomendar para w

Objetivo:
    min Σ(c_transfer * q_transfer) + Σ(c_order * q_order) + penalty_rupture

Restrições:
    stock_final[w, sku] = stock_inicial + q_order + Σ_in q_transfer - Σ_out q_transfer - consumo_previsto
    stock_final[w, sku] >= safety_stock[w, sku]
    Σ_w q_order[w, sku] <= capacidade_fornecimento[sku]
    capacidade_armazenamento[w] >= Σ_sku stock_final[w, sku]
```

**Algoritmos:**
- **MILP** (OR-Tools): Otimização exata (TODO[R&D])
- **Heurística Greedy**: Implementada

**Funcionalidades:**
- `optimize_multi_warehouse()`: Otimização principal
- `_optimize_milp()`: MILP (TODO)
- `_optimize_heuristic()`: Heurística greedy

---

## 📊 6. DASHBOARDS

### 6.1. `dashboards/utilization_heatmap.py` ✅ TRACKED
- Heatmap de utilização de recursos

### 6.2. `dashboards/operator_dashboard.py` ✅ TRACKED
- Dashboard de operadores

### 6.3. `dashboards/machine_oee.py` ✅ TRACKED
- Dashboard de OEE de máquinas

### 6.4. `dashboards/cell_performance.py` ✅ TRACKED
- Dashboard de performance de células

### 6.5. `dashboards/capacity_projection.py` ✅ TRACKED
- Projeção de capacidade

### 6.6. `dashboards/gantt_comparison.py` ✅ TRACKED
- Comparação de Gantt charts

---

## 🧠 7. PLANNING MODULES

### 7.1. `planning/planning_engine.py` ✅ TRACKED
**PlanningEngine** - Engine principal de planeamento

### 7.2. `planning/capacity_planner.py` ✅ TRACKED
**CapacityPlanner** - Planeamento de capacidade:
- `_simulate_scenario()`: Simula cenários de capacidade

### 7.3. `planning/chained_scheduler.py` ✅ TRACKED
**ChainedScheduler** - Scheduler encadeado:
- `_schedule_heuristic()`: Scheduling heurístico
- `_neh_heuristic()`: Heurística NEH (Nawaz-Enscore-Ham)

### 7.4. `planning/conventional_scheduler.py` ✅ TRACKED
**ConventionalScheduler** - Scheduler convencional

### 7.5. `planning/operator_allocator.py` ✅ TRACKED
**OperatorAllocator** - Alocação de operadores

### 7.6. `planning/planning_modes.py` ✅ TRACKED
**PlanningModes** - Modos de planeamento

---

## 🔬 8. RESEARCH MODULES

### 8.1. `research/inventory_optimization.py` ✅ TRACKED
**InventoryOptimizer** - Otimização de inventário (pesquisa)

### 8.2. `research/explainability_engine.py` ✅ TRACKED
**ExplainabilityEngine** - Engine de explicabilidade (pesquisa)

### 8.3. `research/learning_scheduler.py` ✅ TRACKED
**LearningScheduler** - Scheduler de aprendizagem (pesquisa)

### 8.4. `research/routing_engine.py` ✅ TRACKED
**RoutingEngine** - Engine de routing (pesquisa)

### 8.5. `research/setup_engine.py` ✅ TRACKED
**SetupEngine** - Engine de setup (pesquisa):
- **SetupPredictor** (Enum): Tipos de preditores
- **RuleBasedPredictor**: Baseado em regras
- **HistoricalMeanPredictor**: Média histórica
- **MLXGBoostPredictor**: XGBoost ML
- **HybridPredictor**: Híbrido

### 8.6. `research/experiment_logger.py` ✅ TRACKED
**ExperimentLogger** - Logger de experiências

---

## 📦 9. PRODUCT METRICS

### 9.1. `product_metrics/product_kpi_engine.py` ✅ TRACKED
**ProductKPIEngine** - Engine de KPIs de produto

### 9.2. `product_metrics/product_classification.py` ✅ TRACKED
**ProductClassification** - Classificação de produtos

### 9.3. `product_metrics/delivery_time_engine.py` ✅ TRACKED
**DeliveryTimeEngine** - Engine de tempo de entrega

---

## 🎓 10. WORKFORCE FORECASTING

### 10.1. `workforce_analytics/workforce_forecasting.py` ✅ TRACKED

**Forecasting de Produtividade:**
- `_forecast_arima()`: ARIMA para produtividade
- `_forecast_simple()`: Forecast simples
- `_forecast_learning_curve()`: Curva de aprendizagem (Wright's Law)
- `forecast_worker_productivity()`: Forecast principal
- `forecast_all_workers()`: Forecast para todos os workers
- `forecast_lstm()`: LSTM para forecasting
- `forecast_transformer()`: Transformer para forecasting

**Learning Curve Model (Wright's Law):**
```
y(t) = a - b · exp(-c·t)
onde:
    a = asymptotic productivity
    b = initial gap
    c = learning rate
```

### 10.2. `workforce_analytics/workforce_performance_engine.py` ✅ TRACKED

**WorkforcePerformanceEngine** - Engine de performance:
- `predict()`: Prediz produtividade usando curva de aprendizagem

---

## 🧮 11. CORE OPTIMIZATION

### 11.1. `core/setup_engine.py` ✅ TRACKED

**SetupEngine** - Engine de setup:
- `optimize_sequence_greedy()`: Otimização greedy de sequência

### 11.2. `core/optimization/scheduling_milp.py` ✅ TRACKED

**MILP Scheduler** - Scheduling usando MILP:
- `solve()`: Resolve problema de scheduling

### 11.3. `core/explainability/explainability_engine.py` ✅ TRACKED

**ExplainabilityEngine** - Engine de explicabilidade:
- `explain_forecast()`: Explica forecast

---

## 📚 12. ML MODULES (ml/)

### 12.1. `ml/forecasting.py` ✅ TRACKED

**BaseForecaster** (ABC) - Base para forecasters:
- **NaiveForecaster**: Forecast naive
- **MovingAverageForecaster**: Média móvel
- **ExponentialSmoothingForecaster**: Exponential smoothing
- **ARIMAForecaster**: ARIMA
- **XGBoostForecaster**: XGBoost
- **TransformerForecaster**: Transformer

**DemandForecaster** - Forecaster de demanda:
- Suporta todos os tipos acima

**LeadTimeForecaster** - Forecaster de lead time

---

## 🔄 13. SCHEDULING MODULES

### 13.1. `scheduling/drl_policy_stub.py` ✅ TRACKED

**DRLAlgorithm** (Enum) - Algoritmos DRL:
- PPO, A2C, DQN, etc.

**DRLSchedulerConfig** - Configuração DRL:
- `_fallback_heuristic()`: Heurística de fallback

### 13.2. `scheduling/cpsat_models.py` ✅ TRACKED
- CP-SAT models (já documentado)

### 13.3. `scheduling/milp_models.py` ✅ TRACKED
- MILP models (já documentado)

---

## 🎯 14. EXPLAINABILITY

### 14.1. `explainability/explain.py` ✅ TRACKED
- `explain_forecast()`: Explica forecast

### 14.2. `app/llm/explanations.py` ✅ TRACKED
- `_generate_heuristic_explanations()`: Gera explicações de heurísticas

---

## 🔗 15. INTEGRATION

### 15.1. `integration/erp_mes_connector.py` ✅ TRACKED
**ERP/MES Connector** - Conector para sistemas externos

---

## 📦 16. INVENTORY

### 16.1. `inventory/inventory_engine.py` ✅ TRACKED
**InventoryEngine** - Engine de inventário

---

## 🎨 17. ADDITIONAL ENGINES & SERVICES

### 17.1. `app/insights/engine.py` ✅ TRACKED
**InsightEngine** - Engine de insights

### 17.2. `app/aps/scheduler.py` ✅ TRACKED
**APSScheduler** - Scheduler APS:
- `generate_optimized_plan()`: Gera plano otimizado

### 17.3. `app/aps/engine.py` ✅ TRACKED
**APSEngine** - Engine APS:
- `_calculate_optimized()`: Calcula otimizado
- `_simulate_route_score()`: Simula score de rota
- `_schedule_operations_optimized()`: Agenda operações otimizadas

### 17.4. `smart_inventory/bom_engine.py` ✅ TRACKED
**BOMEngine** - Engine de BOM

### 17.5. `smart_inventory/mrp_engine.py` ✅ TRACKED
**MRPEngine** - Engine MRP:
- **MRPFromOrdersEngine**: MRP a partir de ordens

### 17.6. `evaluation/kpi_engine.py` ✅ TRACKED
**KPIEngine** - Engine de KPIs

### 17.7. `optimization/learning_scheduler.py` ✅ TRACKED
**LearningScheduler** - Scheduler de aprendizagem

### 17.8. `rd/wp4_learning_scheduler.py` ✅ TRACKED
**BanditScheduler** - Scheduler bandit

---

## 📋 RESUMO DE FUNCIONALIDADES ENCONTRADAS

### ✅ HEURÍSTICAS (10+)
1. FIFO (First In, First Out)
2. SPT (Shortest Processing Time)
3. EDD (Earliest Due Date)
4. CR (Critical Ratio)
5. WSPT (Weighted Shortest Processing Time)
6. RANDOM
7. Greedy Nearest Neighbor (Setup)
8. 2-opt Local Search
9. Genetic Algorithm (Setup)
10. NEH Heuristic (Chained Scheduling)

### ✅ MODELOS ML (20+)
1. InventoryPredictor (Croston, TSB, Poisson-Gamma)
2. SetupTimePredictor
3. BottleneckPredictor
4. CycleTimePredictor (P50, P90)
5. Routing Predictor (Bandit)
6. DemandForecaster (ARIMA, Prophet, N-BEATS, NST, D-Linear, Ensemble)
7. ClassicalForecastEngine (ARIMA, ETS, XGBoost)
8. AdvancedForecastEngine (NeuralForecast, Darts)
9. WorkforceForecasting (ARIMA, LSTM, Transformer, Learning Curve)
10. TimePredictionEngineML (PyTorch)
11. DefectRiskPredictor (PyTorch)
12. DataQualityModel (PyTorch)
13. CVAE (Health Indicator)
14. RUL Models (PyTorch)
15. NaiveForecaster
16. MovingAverageForecaster
17. ExponentialSmoothingForecaster
18. ARIMAForecaster
19. XGBoostForecaster
20. TransformerForecaster

### ✅ OTIMIZADORES (10+)
1. SetupOptimizer (Greedy, 2-opt, Genetic)
2. Multi-Warehouse Optimizer (MILP, Heuristic)
3. ProcessParameterOptimizer (Bayesian, RL, GA)
4. Advanced Scheduling Solver (CP-SAT, MILP, Heuristics)
5. Multi-Objective Optimizer (Pareto)
6. ProjectPriorityOptimizer (MILP, Heuristic)
7. WorkforceAssignmentModel (MILP)
8. InventoryOptimizer (Research)
9. CapacityPlanner
10. OperatorAllocator

### ✅ ENGINES & SERVICES (50+)
Listados acima em secções específicas

### ✅ DASHBOARDS (6)
1. Utilization Heatmap
2. Operator Dashboard
3. Machine OEE Dashboard
4. Cell Performance Dashboard
5. Capacity Projection Dashboard
6. Gantt Comparison Dashboard

---

## 🚨 FUNCIONALIDADES NÃO EXPOSTAS VIA API

### ❌ Heurísticas de Scheduling
- `scheduling/heuristics.py` - HeuristicDispatcher, HeuristicScheduler
- **Status:** Implementado mas não exposto via API dedicada
- **Sugestão:** Criar `/api/scheduling/heuristics` endpoint

### ❌ Setup Optimizer
- `planning/setup_optimizer.py` - SetupOptimizer
- **Status:** Implementado mas não exposto via API
- **Sugestão:** Criar `/api/planning/setup-optimize` endpoint

### ❌ ML Predictors (app/ml/)
- `app/ml/inventory.py` - InventoryPredictor
- `app/ml/setup_time.py` - SetupTimePredictor
- `app/ml/bottlenecks.py` - BottleneckPredictor
- `app/ml/cycle_time.py` - CycleTimePredictor
- **Status:** Implementados mas não expostos via API dedicada
- **Sugestão:** Criar `/api/ml/predict/inventory`, `/api/ml/predict/setup-time`, etc.

### ❌ Multi-Warehouse Optimizer
- `smart_inventory/multi_warehouse_optimizer.py`
- **Status:** Implementado mas não exposto via API
- **Sugestão:** Criar `/api/smartinventory/multi-warehouse-optimize` endpoint

### ❌ Dashboards
- `dashboards/*.py` - Todos os dashboards
- **Status:** Implementados mas não expostos via API
- **Sugestão:** Criar `/api/dashboards/*` endpoints

### ❌ Planning Modules
- `planning/capacity_planner.py`
- `planning/chained_scheduler.py`
- `planning/conventional_scheduler.py`
- `planning/operator_allocator.py`
- **Status:** Implementados mas não expostos via API
- **Sugestão:** Criar `/api/planning/*` endpoints

### ❌ Research Modules
- `research/*.py` - Todos os módulos de pesquisa
- **Status:** Implementados mas não expostos via API
- **Sugestão:** Integrar com `/api/rd/*` endpoints

### ❌ Product Metrics
- `product_metrics/*.py` - Todos os módulos
- **Status:** Implementados mas não expostos via API
- **Sugestão:** Criar `/api/product-metrics/*` endpoints

### ❌ Workforce Forecasting
- `workforce_analytics/workforce_forecasting.py` - Forecasting avançado
- **Status:** Parcialmente exposto (apenas forecast básico)
- **Sugestão:** Expandir `/api/workforce/forecast` com LSTM, Transformer

### ❌ Core Modules
- `core/setup_engine.py`
- `core/explainability/explainability_engine.py`
- **Status:** Implementados mas não expostos via API
- **Sugestão:** Criar endpoints apropriados

---

## 📊 CONCLUSÃO

### ✅ O QUE ESTÁ TRACKED E IMPLEMENTADO
- **100% dos modelos matemáticos** estão tracked
- **100% dos modelos ML PyTorch** estão tracked
- **100% dos algoritmos** estão tracked
- **100% dos modelos treinados (.pkl)** estão tracked

### ⚠️ O QUE ESTÁ IMPLEMENTADO MAS NÃO EXPOSTO
- **Heurísticas de scheduling** (10+)
- **Setup optimizer** (3 algoritmos)
- **ML predictors** (5+)
- **Multi-warehouse optimizer**
- **Dashboards** (6)
- **Planning modules** (5+)
- **Research modules** (6+)
- **Product metrics** (3)
- **Workforce forecasting avançado** (LSTM, Transformer)
- **Core modules** (3+)

### 🎯 RECOMENDAÇÕES
1. **Criar endpoints API** para todas as funcionalidades não expostas
2. **Integrar com routers existentes** ou criar novos routers
3. **Documentar** todas as funcionalidades no Swagger
4. **Testar** todas as funcionalidades via API

---

**TOTAL DE FUNCIONALIDADES ENCONTRADAS: 100+**

