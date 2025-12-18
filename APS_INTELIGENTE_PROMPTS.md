# 🚀 APS INTELIGENTE ON-PREM - SUPER PROMPTS DE DESENVOLVIMENTO

**Repositório:** https://github.com/nikuframedia-svg/base-  
**Data:** 2025-01-18  
**Objetivo:** Prompts super inovadores e detalhados para desenvolvimento de funcionalidades avançadas

---

## 📋 ÍNDICE DE FUNCIONALIDADES

1. ✅ Planeamento Encadeado (Chained Planning) - **PARCIALMENTE IMPLEMENTADO**
2. ⚠️ LLM Local com Fine-Tuning LoRA - **BÁSICO IMPLEMENTADO**
3. ⚠️ Simulador What-If Conversacional Avançado - **BÁSICO IMPLEMENTADO**
4. ⚠️ Geração Automática de Relatórios pelo LLM - **PARCIALMENTE IMPLEMENTADO**
5. ⚠️ Módulo ML/AutoML Offline Avançado - **PARCIALMENTE IMPLEMENTADO**
6. ⚠️ Visualizações e Dashboards Avançados - **PARCIALMENTE IMPLEMENTADO**
7. ❌ Planeamento de Longo Prazo Estratégico - **NÃO IMPLEMENTADO**
8. ⚠️ Integração ERP/MES Bidirecional Avançada - **BÁSICO IMPLEMENTADO**

---

## 1. ✅ PLANEAMENTO ENCADEADO (CHAINED PLANNING) - MELHORIAS

### Status Atual
- ✅ `backend/planning/chained_scheduler.py` existe (617 linhas)
- ✅ Modelo MILP básico implementado
- ⚠️ Faltam: otimização de buffers dinâmica, sincronização multi-cadeia, WIP optimization

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: PLANEAMENTO ENCADEADO AVANÇADO COM OTIMIZAÇÃO DINÂMICA DE BUFFERS

## CONTEXTO
Implementar um sistema de planeamento encadeado (Chained Planning) que sincroniza múltiplas máquinas/etapas em fluxo contínuo, com otimização dinâmica de buffers e gestão de WIP (Work In Progress).

## MODELO MATEMÁTICO AVANÇADO

### 1. Formulação MILP Multi-Objetivo com Buffers Dinâmicos

**Sets:**
- J = {1, ..., n} : Jobs (ordens)
- M = {1, ..., m} : Máquinas na cadeia
- K = {1, ..., k} : Cadeias de produção
- T = {1, ..., T} : Períodos temporais discretos

**Variables:**
- S_{j,k,m} : Start time do job j na cadeia k, máquina m
- C_{j,k,m} : Completion time do job j na cadeia k, máquina m
- y_{i,j,k,m} ∈ {0,1} : 1 se job i precede job j na máquina m da cadeia k
- B_{k,m,t} ≥ 0 : Buffer size (WIP) na máquina m da cadeia k no período t
- b_{k,m} ≥ 0 : Buffer time otimizado entre máquina m e m+1 na cadeia k
- w_{j,k} ∈ {0,1} : 1 se job j é alocado à cadeia k

**Parameters:**
- p_{j,k,m} : Processing time do job j na máquina m da cadeia k
- d_j : Due date do job j
- b_min_{k,m} : Buffer mínimo entre máquina m e m+1
- b_max_{k,m} : Buffer máximo permitido
- WIP_max_{k,m} : Capacidade máxima de WIP na máquina m
- c_buffer : Custo de manter buffer (€/unidade/hora)
- c_tardiness : Custo de atraso (€/hora)
- c_makespan : Peso do makespan no objetivo

**Constraints:**

(1) Completion: C_{j,k,m} = S_{j,k,m} + p_{j,k,m}  ∀j,k,m

(2) Precedence encadeada: S_{j,k,m+1} ≥ C_{j,k,m} + b_{k,m}  ∀j,k,m<|M_k|

(3) No overlap: S_{j,k,m} ≥ C_{i,k,m} - M(1 - y_{i,j,k,m})  ∀i≠j,k,m

(4) Sequencing: y_{i,j,k,m} + y_{j,i,k,m} = 1  ∀i<j,k,m

(5) Buffer bounds: b_min_{k,m} ≤ b_{k,m} ≤ b_max_{k,m}  ∀k,m

(6) WIP constraint: B_{k,m,t} ≤ WIP_max_{k,m}  ∀k,m,t

(7) WIP dynamics: B_{k,m,t+1} = B_{k,m,t} + arrivals_{k,m,t} - completions_{k,m,t}

(8) Single chain assignment: Σ_k w_{j,k} = 1  ∀j

**Objective Function (Multi-Objective):**

min  α₁·C_max + α₂·Σ_j w_j·max(0, C_{j,k,|M_k|} - d_j) + α₃·Σ_{k,m} c_buffer·B_{k,m} + α₄·Σ_{k,m} |b_{k,m} - b_optimal_{k,m}|

Onde:
- C_max = max_{j,k} C_{j,k,|M_k|}  (makespan global)
- b_optimal_{k,m} = f(WIP_{k,m}, throughput_{k,m})  (buffer ótimo calculado dinamicamente)

### 2. Algoritmo de Otimização de Buffers Dinâmica

Implementar algoritmo híbrido:
- **Fase 1**: Resolver MILP com buffers fixos (valores iniciais)
- **Fase 2**: Usar **Gradient-Based Optimization** para ajustar buffers:
  - Calcular gradiente: ∂(objective)/∂b_{k,m}
  - Aplicar **Adam Optimizer** adaptado para buffers discretos
  - Iterar até convergência ou timeout

**Fórmula de Buffer Ótimo:**
b_optimal_{k,m} = argmin_b [c_buffer·b + c_tardiness·E[Tardiness|b] + c_WIP·E[WIP|b]]

Onde E[·] é esperança calculada via simulação estocástica.

### 3. Sincronização Multi-Cadeia

Para múltiplas cadeias que convergem/divergem:

**Convergence Point:**
- Jobs de cadeias diferentes chegam ao mesmo recurso
- Usar **Priority Queue** com **Critical Ratio** dinâmico
- CR_{j} = (d_j - t_now) / remaining_processing_time

**Divergence Point:**
- Jobs saem de uma máquina para múltiplas cadeias
- Usar **Load Balancing Algorithm**:
  - Balancear carga: min Σ_k |load_k - avg_load|
  - Considerar capacidades e tempos de setup

## IMPLEMENTAÇÃO TÉCNICA

### Arquitetura
1. **ChainedSchedulerAdvanced** class
   - Herda de `ChainedScheduler` existente
   - Adiciona métodos: `optimize_buffers()`, `sync_multi_chain()`, `calculate_wip()`

2. **BufferOptimizer** class
   - Método: `optimize_dynamic_buffers(chain_config, historical_data)`
   - Usa scipy.optimize.minimize com método 'L-BFGS-B'
   - Integra simulação estocástica para E[·]

3. **MultiChainSynchronizer** class
   - Método: `synchronize_chains(chains, convergence_points, divergence_points)`
   - Implementa algoritmo de balanceamento de carga

### Integração com LLM
- LLM interpreta comandos: "Ativa modo encadeado A→B→C com buffer 30min"
- LLM explica decisões: "Buffer otimizado para 45min para reduzir WIP em 20%"

## TESTES
- Testar com 3 cadeias, 5 máquinas cada
- Validar redução de makespan vs planeamento independente
- Verificar WIP dentro de limites
- Medir tempo de execução (< 60s para 100 jobs)

## FICHEIRO DE SAÍDA
`backend/planning/chained_scheduler_advanced.py`
```

---

## 2. ⚠️ LLM LOCAL COM FINE-TUNING LORA - MELHORIAS

### Status Atual
- ✅ `backend/app/llm/local.py` existe (básico)
- ❌ Falta: Fine-tuning LoRA, vector database, contexto industrial

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: LLM LOCAL AVANÇADO COM FINE-TUNING LORA E VECTOR DATABASE

## CONTEXTO
Implementar um sistema LLM local (LLaMA/Mistral) com fine-tuning LoRA para domínio industrial, integrado com vector database para contexto específico da fábrica.

## ARQUITETURA AVANÇADA

### 1. Fine-Tuning LoRA (Low-Rank Adaptation)

**Modelo Base:**
- LLaMA 2 7B ou Mistral 7B (quantizado 4-bit)
- Rodar localmente via llama.cpp ou Ollama

**LoRA Configuration:**
- Rank r = 16 (trade-off qualidade/velocidade)
- Alpha = 32 (scaling factor)
- Target modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
- Learning rate: 1e-4
- Batch size: 4
- Epochs: 3-5

**Dataset de Treino:**
- 1000+ exemplos de comandos industriais
- Formato: {"instruction": "...", "input": "...", "output": "..."}
- Exemplos:
  - "Adiciona máquina 305B com tempo ciclo 20% mais rápido"
  - "Explica por que ordem #1234 está atrasada"
  - "Compara cenário baseline vs novo cenário"

**Training Script:**
```python
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    load_in_4bit=True,
    device_map="auto"
)

model = get_peft_model(model, lora_config)
# Training loop...
```

### 2. Vector Database para Contexto Industrial

**Embeddings:**
- Usar `sentence-transformers` (all-MiniLM-L6-v2)
- Embeddings de: ordens, máquinas, produtos, histórico de decisões

**Vector Store:**
- Usar **ChromaDB** ou **FAISS** (local, on-prem)
- Indexar: 10k+ documentos industriais
- Similarity search: cosine similarity

**RAG (Retrieval-Augmented Generation):**
1. Query do utilizador → embedding
2. Vector search → top 5 documentos relevantes
3. Context injection → prompt com contexto
4. LLM gera resposta baseada em contexto

**Exemplo:**
```python
from sentence_transformers import SentenceTransformer
import chromadb

# Inicializar
embedder = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client()
collection = client.create_collection("industrial_knowledge")

# Indexar conhecimento
docs = ["Máquina 305: tempo ciclo 45min, setup 15min", ...]
embeddings = embedder.encode(docs)
collection.add(embeddings=embeddings, documents=docs)

# Query
query_embedding = embedder.encode("Qual tempo ciclo máquina 305?")
results = collection.query(query_embeddings=[query_embedding], n_results=3)
```

### 3. Prompt Engineering Avançado

**Template de Prompt:**
```
Você é um assistente especializado em planeamento de produção industrial (APS).

CONTEXTO DA FÁBRICA:
{context_from_vector_db}

DADOS ATUAIS DO PLANO:
{current_plan_summary}

HISTÓRICO DE DECISÕES:
{recent_decisions}

INSTRUÇÃO DO UTILIZADOR:
{user_query}

RESPOSTA (seja técnico mas claro):
```

### 4. Integração com APS

**Endpoints:**
- `/api/llm/chat` - Chat geral
- `/api/llm/explain` - Explicar decisão
- `/api/llm/command` - Interpretar comando NL → ação APS
- `/api/llm/report` - Gerar relatório automático

**Command Parser:**
```python
class IndustrialCommandParser:
    def parse(self, text: str) -> APSAction:
        # Usar LLM para extrair:
        # - Tipo de ação (add_machine, remove_machine, etc.)
        # - Parâmetros (machine_id, date, etc.)
        # - Validação de segurança
```

## IMPLEMENTAÇÃO

### Ficheiros a Criar:
1. `backend/app/llm/lora_trainer.py` - Fine-tuning LoRA
2. `backend/app/llm/vector_store.py` - Vector database
3. `backend/app/llm/rag_engine.py` - RAG implementation
4. `backend/app/llm/command_parser.py` - NL command parser
5. `backend/app/llm/prompt_templates.py` - Templates avançados

### Dependências:
- `peft` - LoRA fine-tuning
- `sentence-transformers` - Embeddings
- `chromadb` ou `faiss-cpu` - Vector store
- `llama-cpp-python` ou `ollama` - LLM local

## TESTES
- Validar compreensão de termos industriais
- Testar RAG com queries específicas
- Medir latência (< 2s por resposta)
- Validar segurança (não executar comandos perigosos)

## FICHEIRO DE SAÍDA
`backend/app/llm/advanced_llm_system.py`
```

---

## 3. ⚠️ SIMULADOR WHAT-IF CONVERSACIONAL AVANÇADO

### Status Atual
- ✅ `backend/app/api/whatif.py` existe (básico)
- ❌ Falta: Parser NL avançado, reconfiguração dinâmica, comparação visual

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: SIMULADOR WHAT-IF CONVERSACIONAL COM RECONFIGURAÇÃO DINÂMICA

## CONTEXTO
Implementar um simulador What-If que permite reconfigurar a fábrica via comandos em linguagem natural, recalcular planos instantaneamente e comparar cenários.

## MODELO MATEMÁTICO DE RECONFIGURAÇÃO

### 1. Formalização de Alterações de Cenário

**State Space:**
S = {M, R, C, P, T, O}

Onde:
- M = {m₁, ..., mₙ} : Conjunto de máquinas
- R = {r₁, ..., rₖ} : Conjunto de rotas
- C = {c₁, ..., cₗ} : Calendários (turnos, manutenção)
- P = {p₁, ..., pₘ} : Parâmetros de processo
- T = {t₁, ..., tₒ} : Tempos (ciclo, setup)
- O = {o₁, ..., oₚ} : Operadores

**Transition Function:**
δ: S × Action → S'

**Actions:**
- ADD_MACHINE(m, specs)
- REMOVE_MACHINE(m, date)
- REPLACE_MACHINE(m_old, m_new, date)
- MODIFY_PARAMETER(p, new_value, date)
- CHANGE_ROUTING(product, old_route, new_route)
- ADD_SHIFT(machine, shift_config, date)
- REMOVE_SHIFT(machine, shift_id, date)

### 2. Algoritmo de Reconfiguração Incremental

**Incremental Replanning:**
- Em vez de recalcular tudo, recalcular apenas afetados
- Usar **Dependency Graph** para identificar impactos

**Dependency Graph:**
G = (V, E) onde:
- V = {jobs, machines, operations}
- E = {(u,v) | u depende de v}

**Algoritmo:**
```python
def incremental_replan(base_plan, changes):
    affected = set()
    for change in changes:
        affected.update(get_dependent_nodes(change))
    
    # Recalcular apenas afetados
    new_plan = base_plan.copy()
    for node in affected:
        new_plan[node] = reschedule(node, constraints)
    
    return new_plan
```

### 3. Comparação de Cenários (Métricas)

**Métricas de Comparação:**
- Makespan: ΔC_max = C_max_new - C_max_base
- Throughput: ΔTP = TP_new - TP_base
- Utilization: ΔU_m = U_m_new - U_m_base
- Tardiness: ΔT = Σ(max(0, C_j - d_j))
- WIP: ΔWIP = WIP_new - WIP_base
- Cost: ΔCost = Cost_new - Cost_base

**Score de Melhoria:**
Score = w₁·(ΔTP/TP_base) + w₂·(-ΔT/T_base) + w₃·(-ΔCost/Cost_base)

### 4. Natural Language Command Parser

**Usar LLM + Structured Output:**
```python
class WhatIfCommandParser:
    def parse(self, text: str) -> List[Action]:
        prompt = f"""
        Parse o seguinte comando de reconfiguração industrial:
        "{text}"
        
        Extraia ações no formato JSON:
        {{
            "actions": [
                {{
                    "type": "ADD_MACHINE|REMOVE_MACHINE|...",
                    "target": "machine_id",
                    "params": {{...}},
                    "date": "YYYY-MM-DD"
                }}
            ]
        }}
        """
        
        response = llm.generate(prompt)
        return parse_json(response)
```

## IMPLEMENTAÇÃO

### Classes Principais:

1. **WhatIfSimulator** class
   - `simulate_scenario(changes: List[Action]) -> ScenarioResult`
   - `compare_scenarios(base, new) -> ComparisonReport`
   - `apply_changes(base_plan, changes) -> new_plan`

2. **ScenarioReconfigurator** class
   - `add_machine(specs) -> Action`
   - `remove_machine(machine_id, date) -> Action`
   - `modify_parameter(param, value, date) -> Action`
   - `change_routing(product, new_route) -> Action`

3. **ScenarioComparator** class
   - `compare_metrics(base, new) -> ComparisonMetrics`
   - `identify_bottlenecks(base, new) -> List[Bottleneck]`
   - `calculate_improvement_score(base, new) -> float`

4. **NLCommandParser** class
   - `parse_command(text: str) -> List[Action]`
   - `validate_actions(actions) -> ValidationResult`

### Integração com LLM:
- LLM interpreta: "Adiciona máquina 305B 20% mais rápida a partir de Maio"
- LLM explica: "Máquina 305B reduz makespan em 15% mas cria novo gargalo em 310"

## TESTES
- Testar 10+ comandos NL diferentes
- Validar reconfiguração incremental (< 5s)
- Verificar comparação de métricas
- Testar segurança (não permitir ações destrutivas sem confirmação)

## FICHEIRO DE SAÍDA
`backend/simulation/whatif_advanced.py`
```

---

## 4. ⚠️ GERAÇÃO AUTOMÁTICA DE RELATÓRIOS PELO LLM

### Status Atual
- ⚠️ Parcialmente implementado em `backend/app/insights/engine.py`
- ❌ Falta: Templates avançados, análise financeira, relatórios executivos

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: GERAÇÃO AUTOMÁTICA DE RELATÓRIOS EXECUTIVOS E TÉCNICOS

## CONTEXTO
Implementar sistema de geração automática de relatórios usando LLM, com templates avançados, análise financeira e visualizações integradas.

## ARQUITETURA DE GERAÇÃO DE RELATÓRIOS

### 1. Template System Avançado

**Tipos de Relatórios:**
- Executive Summary (1 página)
- Technical Analysis (detalhado)
- Comparison Report (baseline vs cenário)
- Financial Impact Analysis
- Bottleneck Analysis
- Improvement Recommendations

**Template Structure:**
```python
class ReportTemplate:
    sections: List[Section]
    metrics: List[Metric]
    visualizations: List[VizConfig]
    llm_prompts: Dict[str, str]
```

### 2. Análise Financeira Automática

**Métricas Financeiras:**
- ROI (Return on Investment)
- Payback Period
- NPV (Net Present Value)
- Cost per Unit
- Margin Impact

**Cálculos:**
```python
def calculate_roi(investment, annual_savings, years=5):
    total_savings = sum([annual_savings * (1 + discount_rate)**-i 
                        for i in range(1, years+1)])
    roi = (total_savings - investment) / investment * 100
    return roi

def calculate_payback(investment, monthly_savings):
    return investment / monthly_savings  # meses
```

### 3. LLM-Powered Report Generation

**Prompt Template:**
```
Você é um analista industrial experiente. Gere um relatório executivo baseado nos dados:

DADOS DO PLANO BASE:
{base_plan_metrics}

DADOS DO NOVO CENÁRIO:
{new_scenario_metrics}

COMPARAÇÃO:
{comparison_metrics}

Gere um relatório com:
1. Executive Summary (3 parágrafos)
2. Principais Melhorias (top 5)
3. Principais Riscos (top 3)
4. Recomendações (3-5 ações)
5. Análise Financeira (ROI, Payback)

Formato: Markdown profissional
```

### 4. Visualizações Integradas

**Gerar gráficos localmente:**
- Gantt comparativo (matplotlib/plotly)
- Heatmaps de utilização
- Gráficos de barras (antes/depois)
- Projeções temporais

**Integração:**
```python
def generate_report_with_viz(data, template):
    report_text = llm.generate_report(data, template)
    visualizations = generate_charts(data)
    return combine_report(report_text, visualizations)
```

## IMPLEMENTAÇÃO

### Classes:

1. **ReportGenerator** class
   - `generate_executive_summary(plan_data) -> str`
   - `generate_technical_analysis(plan_data) -> str`
   - `generate_comparison_report(base, new) -> str`
   - `generate_financial_analysis(scenario) -> FinancialReport`

2. **FinancialAnalyzer** class
   - `calculate_roi(investment, savings) -> float`
   - `calculate_payback(investment, monthly_savings) -> float`
   - `estimate_cost_impact(changes) -> CostImpact`

3. **ReportTemplateEngine** class
   - `load_template(template_name) -> Template`
   - `render_template(template, data) -> str`
   - `add_visualization(report, viz_config) -> Report`

## TESTES
- Validar qualidade dos relatórios (review manual)
- Testar cálculos financeiros (validação com Excel)
- Verificar integração de visualizações
- Medir tempo de geração (< 10s)

## FICHEIRO DE SAÍDA
`backend/reporting/llm_report_generator.py`
```

---

## 5. ⚠️ MÓDULO ML/AUTOML OFFLINE AVANÇADO

### Status Atual
- ⚠️ Parcialmente implementado (XGBoost, ARIMA básicos)
- ❌ Falta: AutoML completo (H2O.ai), detecção de anomalias avançada, ensemble methods

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: AUTOML OFFLINE AVANÇADO COM H2O.AI E ENSEMBLE METHODS

## CONTEXTO
Implementar módulo AutoML completo usando H2O.ai para seleção automática de modelos, com detecção de anomalias e ensemble methods.

## ARQUITETURA AUTOML

### 1. H2O.ai AutoML Integration

**Configuração:**
```python
import h2o
from h2o.automl import H2OAutoML

h2o.init()

# Preparar dados
train_frame = h2o.H2OFrame(train_data)
test_frame = h2o.H2OFrame(test_data)

# AutoML
aml = H2OAutoML(
    max_models=20,
    max_runtime_secs=3600,  # 1 hora
    seed=42,
    stopping_metric="RMSE",
    stopping_tolerance=0.001,
    stopping_rounds=3,
    sort_metric="RMSE"
)

aml.train(
    x=features,
    y=target,
    training_frame=train_frame,
    validation_frame=test_frame
)

# Melhor modelo
best_model = aml.leader
```

### 2. Ensemble Methods

**Stacking Ensemble:**
- Base models: XGBoost, Random Forest, Neural Network
- Meta-learner: Linear Regression ou XGBoost
- Cross-validation para evitar overfitting

**Blending:**
- Treinar modelos em diferentes folds
- Combinar predições com pesos otimizados

**Código:**
```python
class EnsemblePredictor:
    def __init__(self):
        self.base_models = [
            XGBoostRegressor(),
            RandomForestRegressor(),
            MLPRegressor()
        ]
        self.meta_learner = LinearRegression()
    
    def fit(self, X, y):
        # Treinar base models
        base_predictions = []
        for model in self.base_models:
            model.fit(X, y)
            pred = model.predict(X)
            base_predictions.append(pred)
        
        # Treinar meta-learner
        meta_X = np.column_stack(base_predictions)
        self.meta_learner.fit(meta_X, y)
    
    def predict(self, X):
        base_preds = [m.predict(X) for m in self.base_models]
        meta_X = np.column_stack(base_preds)
        return self.meta_learner.predict(meta_X)
```

### 3. Detecção de Anomalias Avançada

**Isolation Forest + LSTM Autoencoder:**
```python
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Model

# Isolation Forest
iso_forest = IsolationForest(contamination=0.1)
anomalies_iso = iso_forest.fit_predict(data)

# LSTM Autoencoder
class LSTMAutoencoder:
    def __init__(self, seq_length=10, latent_dim=32):
        # Encoder
        encoder_input = Input(shape=(seq_length, n_features))
        encoded = LSTM(latent_dim)(encoder_input)
        
        # Decoder
        decoded = RepeatVector(seq_length)(encoded)
        decoded = LSTM(n_features, return_sequences=True)(decoded)
        
        self.autoencoder = Model(encoder_input, decoded)
        self.autoencoder.compile(optimizer='adam', loss='mse')
    
    def detect_anomalies(self, data, threshold=0.1):
        reconstructed = self.autoencoder.predict(data)
        mse = np.mean((data - reconstructed)**2, axis=1)
        anomalies = mse > threshold
        return anomalies
```

### 4. Previsões Avançadas

**Time Series Forecasting com AutoML:**
- Auto-ARIMA (pmdarima)
- Prophet (Facebook)
- N-BEATS (NeuralForecast)
- Auto-seleção baseada em AIC/BIC

**Código:**
```python
from pmdarima import auto_arima
from prophet import Prophet
from neuralforecast import NeuralForecast
from neuralforecast.models import NBEATS

def auto_forecast(series, horizon=12):
    # Tentar Auto-ARIMA
    arima_model = auto_arima(series, seasonal=True, m=12)
    arima_forecast = arima_model.predict(horizon)
    
    # Tentar Prophet
    prophet_df = pd.DataFrame({
        'ds': series.index,
        'y': series.values
    })
    prophet_model = Prophet()
    prophet_model.fit(prophet_df)
    prophet_forecast = prophet_model.predict(
        prophet_model.make_future_dataframe(periods=horizon)
    )
    
    # Tentar N-BEATS
    nbeats = NBEATS(h=horizon, input_size=24)
    nbeats_forecast = nbeats.predict(series)
    
    # Ensemble (média ponderada)
    final_forecast = (
        0.4 * arima_forecast +
        0.3 * prophet_forecast +
        0.3 * nbeats_forecast
    )
    
    return final_forecast
```

## IMPLEMENTAÇÃO

### Classes:

1. **AutoMLPredictor** class
   - `train_automl(data, target) -> H2OAutoML`
   - `predict(model, data) -> predictions`
   - `get_feature_importance(model) -> Dict`

2. **EnsemblePredictor** class
   - `create_ensemble(base_models, meta_learner) -> Ensemble`
   - `fit_ensemble(X, y) -> fitted_ensemble`
   - `predict_ensemble(X) -> predictions`

3. **AnomalyDetector** class
   - `detect_isolation_forest(data) -> anomalies`
   - `detect_lstm_autoencoder(data) -> anomalies`
   - `explain_anomalies(anomalies, data) -> explanations`

4. **AdvancedForecaster** class
   - `auto_forecast(series, horizon) -> forecast`
   - `compare_models(series) -> best_model`
   - `ensemble_forecast(series, models) -> forecast`

## TESTES
- Validar acurácia AutoML vs modelos manuais
- Testar detecção de anomalias (F1-score > 0.8)
- Verificar ensemble performance
- Medir tempo de treino (< 1h para datasets normais)

## FICHEIRO DE SAÍDA
`backend/ml/automl_advanced.py`
```

---

## 6. ⚠️ VISUALIZAÇÕES E DASHBOARDS AVANÇADOS

### Status Atual
- ⚠️ Dashboards básicos existem
- ❌ Falta: Gantt comparativo, heatmaps interativos, projeções visuais

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: DASHBOARDS AVANÇADOS COM VISUALIZAÇÕES INTERATIVAS

## CONTEXTO
Implementar dashboards avançados com visualizações comparativas, heatmaps interativos e projeções visuais.

## VISUALIZAÇÕES AVANÇADAS

### 1. Gantt Comparativo Interativo

**Usar Plotly:**
```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_comparative_gantt(base_plan, new_plan):
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Plano Base', 'Novo Cenário'),
        vertical_spacing=0.1
    )
    
    # Base plan
    for job in base_plan.jobs:
        fig.add_trace(
            go.Bar(
                x=[job.start, job.duration],
                y=[job.machine],
                name=f"Base: {job.id}",
                marker_color='blue',
                base=job.start
            ),
            row=1, col=1
        )
    
    # New plan
    for job in new_plan.jobs:
        color = 'green' if job.changed else 'orange'
        fig.add_trace(
            go.Bar(
                x=[job.start, job.duration],
                y=[job.machine],
                name=f"New: {job.id}",
                marker_color=color,
                base=job.start
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        title="Comparação de Planos",
        xaxis_title="Tempo",
        yaxis_title="Máquinas",
        height=800
    )
    
    return fig
```

### 2. Heatmap de Utilização Interativo

```python
def create_utilization_heatmap(machines, time_periods, utilization_data):
    fig = go.Figure(data=go.Heatmap(
        z=utilization_data,
        x=time_periods,
        y=machines,
        colorscale='RdYlGn',
        colorbar=dict(title="Utilização %"),
        hovertemplate='Máquina: %{y}<br>Período: %{x}<br>Utilização: %{z}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Heatmap de Utilização por Máquina",
        xaxis_title="Período",
        yaxis_title="Máquinas",
        height=600
    )
    
    return fig
```

### 3. Projeções Anuais Visuais

```python
def create_annual_projection(capacity, demand, months):
    fig = go.Figure()
    
    # Capacity line
    fig.add_trace(go.Scatter(
        x=months,
        y=capacity,
        mode='lines+markers',
        name='Capacidade',
        line=dict(color='green', width=2)
    ))
    
    # Demand line
    fig.add_trace(go.Scatter(
        x=months,
        y=demand,
        mode='lines+markers',
        name='Demanda',
        line=dict(color='red', width=2)
    ))
    
    # Fill area between
    fig.add_trace(go.Scatter(
        x=months + months[::-1],
        y=capacity + demand[::-1],
        fill='toself',
        fillcolor='rgba(255,0,0,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        name='Déficit'
    ))
    
    fig.update_layout(
        title="Projeção Anual: Capacidade vs Demanda",
        xaxis_title="Mês",
        yaxis_title="Unidades",
        height=500
    )
    
    return fig
```

### 4. Dashboard de Células Encadeadas

```python
def create_chain_dashboard(chains_data):
    fig = make_subplots(
        rows=len(chains_data), cols=1,
        subplot_titles=[f"Cadeia {c.id}" for c in chains_data]
    )
    
    for idx, chain in enumerate(chains_data):
        # WIP por máquina na cadeia
        machines = chain.machines
        wip_values = [chain.wip[m] for m in machines]
        
        fig.add_trace(
            go.Bar(
                x=machines,
                y=wip_values,
                name=f"WIP - {chain.id}",
                marker_color='steelblue'
            ),
            row=idx+1, col=1
        )
        
        # Throughput
        fig.add_trace(
            go.Scatter(
                x=machines,
                y=chain.throughput,
                mode='lines+markers',
                name=f"Throughput - {chain.id}",
                line=dict(color='orange', width=2),
                yaxis=f'y{idx+2}'
            ),
            row=idx+1, col=1
        )
    
    fig.update_layout(height=300 * len(chains_data))
    return fig
```

## IMPLEMENTAÇÃO

### Classes:

1. **AdvancedDashboardGenerator** class
   - `generate_comparative_gantt(base, new) -> Figure`
   - `generate_utilization_heatmap(data) -> Figure`
   - `generate_annual_projection(capacity, demand) -> Figure`
   - `generate_chain_dashboard(chains) -> Figure`

2. **InteractiveVisualizer** class
   - `create_interactive_plot(fig) -> HTML`
   - `export_to_png(fig, filename) -> None`
   - `export_to_pdf(fig, filename) -> None`

## TESTES
- Validar renderização de gráficos
- Testar interatividade (hover, zoom)
- Verificar exportação (PNG, PDF)
- Medir performance (< 2s para gerar dashboard)

## FICHEIRO DE SAÍDA
`backend/dashboards/advanced_visualizations.py`
```

---

## 7. ❌ PLANEAMENTO DE LONGO PRAZO ESTRATÉGICO

### Status Atual
- ❌ **NÃO IMPLEMENTADO**
- ⚠️ Existe `backend/dashboards/capacity_projection.py` (básico)

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: PLANEAMENTO ESTRATÉGICO DE LONGO PRAZO (ANUAL/PLURIANUAL)

## CONTEXTO
Implementar sistema de planeamento estratégico de longo prazo (horizonte anual/plurianual) com simulação de investimentos, avaliação de capacidade futura e cenários de crescimento.

## MODELO MATEMÁTICO ESTRATÉGICO

### 1. Capacity Planning Multi-Periodo

**Horizonte Temporal:**
- T = {1, ..., T} : Períodos (meses/trimestres)
- T = 12 (anual) ou T = 36 (3 anos)

**Variables:**
- C_{m,t} ≥ 0 : Capacidade disponível da máquina m no período t
- I_{m,t} ∈ {0,1} : 1 se investimento em máquina m no período t
- D_{p,t} ≥ 0 : Demanda do produto p no período t
- P_{p,t} ≥ 0 : Produção do produto p no período t
- S_{p,t} ≥ 0 : Stock do produto p no período t

**Parameters:**
- cap_base_{m} : Capacidade base da máquina m
- cap_new_{m} : Capacidade de nova máquina m
- cost_inv_{m} : Custo de investimento em máquina m
- demand_forecast_{p,t} : Previsão de demanda
- growth_rate : Taxa de crescimento anual
- discount_rate : Taxa de desconto

**Constraints:**

(1) Capacity: C_{m,t} = cap_base_{m} + Σ_{s≤t} I_{m,s} · cap_new_{m}

(2) Production capacity: Σ_p P_{p,t} · time_{p,m} ≤ C_{m,t}  ∀m,t

(3) Demand satisfaction: P_{p,t} + S_{p,t-1} ≥ D_{p,t} + S_{p,t}  ∀p,t

(4) Stock balance: S_{p,t} = S_{p,t-1} + P_{p,t} - D_{p,t}  ∀p,t

(5) Investment budget: Σ_{m,t} I_{m,t} · cost_inv_{m} ≤ budget_t  ∀t

**Objective:**
min Σ_{m,t} I_{m,t} · cost_inv_{m} · (1 + discount_rate)^{-t} + 
    Σ_{p,t} c_shortage · max(0, D_{p,t} - P_{p,t} - S_{p,t-1}) +
    Σ_{p,t} c_holding · S_{p,t}

### 2. Demand Forecasting Estratégico

**Modelo de Crescimento:**
D_{p,t} = D_{p,0} · (1 + growth_rate_p)^{t/12} · seasonality_{t mod 12}

**Sazonalidade:**
seasonality_{m} = 1 + A · sin(2πm/12 + φ)

**Uncertainty:**
D_{p,t} ~ Normal(μ_{p,t}, σ_{p,t})

Onde σ_{p,t} = μ_{p,t} · CV (coefficient of variation)

### 3. Investment Optimization

**NPV Calculation:**
NPV = Σ_{t=0}^{T} (CashFlow_t) / (1 + r)^t

**ROI:**
ROI = (Total_Benefits - Total_Cost) / Total_Cost · 100

**Payback Period:**
Payback = min{t | Σ_{s=0}^{t} CashFlow_s ≥ 0}

### 4. Scenario Analysis

**Cenários:**
- Baseline: crescimento 5%
- Optimistic: crescimento 10%
- Pessimistic: crescimento 2%
- Stagflation: crescimento 0%, inflação alta

**Monte Carlo Simulation:**
```python
def monte_carlo_scenario(demand_dist, capacity_options, n_simulations=1000):
    results = []
    for _ in range(n_simulations):
        # Sample demanda
        demand_sample = demand_dist.sample()
        
        # Calcular capacidade necessária
        required_capacity = calculate_required_capacity(demand_sample)
        
        # Escolher investimento ótimo
        investment = optimize_investment(required_capacity, capacity_options)
        
        # Calcular NPV
        npv = calculate_npv(investment, demand_sample)
        results.append(npv)
    
    return {
        'mean_npv': np.mean(results),
        'std_npv': np.std(results),
        'p5_npv': np.percentile(results, 5),
        'p95_npv': np.percentile(results, 95)
    }
```

## IMPLEMENTAÇÃO

### Classes:

1. **StrategicPlanner** class
   - `create_strategic_plan(horizon_years, demand_forecast) -> StrategicPlan`
   - `optimize_investments(capacity_options, budget) -> InvestmentPlan`
   - `evaluate_scenarios(scenarios) -> ScenarioComparison`

2. **LongTermForecaster** class
   - `forecast_demand(historical_data, growth_rate, horizon) -> DemandForecast`
   - `add_seasonality(forecast, seasonality_params) -> Forecast`
   - `add_uncertainty(forecast, cv) -> ProbabilisticForecast`

3. **InvestmentOptimizer** class
   - `optimize_capacity_investments(demand, options, budget) -> InvestmentPlan`
   - `calculate_npv(investment, cashflows, discount_rate) -> float`
   - `calculate_roi(investment, benefits) -> float`

4. **ScenarioAnalyzer** class
   - `create_scenarios(base_forecast, variations) -> List[Scenario]`
   - `monte_carlo_simulation(scenarios, n_simulations) -> MCResults`
   - `compare_scenarios(scenarios) -> ComparisonReport`

## TESTES
- Validar previsões de longo prazo (backtesting)
- Testar otimização de investimentos (validação com Excel)
- Verificar cenários (sanity check)
- Medir tempo de cálculo (< 5min para 3 anos)

## FICHEIRO DE SAÍDA
`backend/planning/strategic_planner.py`
```

---

## 8. ⚠️ INTEGRAÇÃO ERP/MES BIDIRECIONAL AVANÇADA

### Status Atual
- ⚠️ Básico existe em `backend/integration/erp_mes_connector.py`
- ❌ Falta: Sincronização em tempo real, APIs RESTful, webhooks

### 🎯 PROMPT SUPER INOVADOR

```
# PROMPT: INTEGRAÇÃO ERP/MES BIDIRECIONAL COM SINCRONIZAÇÃO EM TEMPO REAL

## CONTEXTO
Implementar integração bidirecional avançada com ERP/MES, incluindo sincronização em tempo real, APIs RESTful e webhooks.

## ARQUITETURA DE INTEGRAÇÃO

### 1. Data Synchronization Protocol

**Change Data Capture (CDC):**
- Monitorar mudanças em ERP/MES
- Usar triggers SQL ou polling
- Aplicar apenas mudanças incrementais

**Conflict Resolution:**
- Last-Write-Wins (LWW)
- Timestamp-based
- Version vectors para resolução distribuída

### 2. RESTful API Design

**Endpoints:**

```
POST /api/integration/erp/import-orders
GET  /api/integration/erp/orders
POST /api/integration/erp/export-plan
GET  /api/integration/mes/status
POST /api/integration/mes/update-execution
GET  /api/integration/mes/machine-status
```

**Data Models:**
```python
class ERPOrder:
    order_id: str
    product_id: str
    quantity: int
    due_date: datetime
    priority: str
    status: str

class MESExecution:
    operation_id: str
    machine_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # running, completed, stopped
    actual_duration: Optional[float]
```

### 3. Webhook System

**Event Types:**
- order_created
- order_updated
- order_cancelled
- execution_started
- execution_completed
- machine_down
- material_shortage

**Webhook Handler:**
```python
class WebhookHandler:
    def handle_order_created(self, event):
        order = parse_order(event.data)
        self.aps.add_order(order)
        self.aps.replan()
    
    def handle_execution_completed(self, event):
        execution = parse_execution(event.data)
        self.aps.update_execution_status(execution)
        self.aps.adjust_plan()
```

### 4. Real-Time Synchronization

**WebSocket Connection:**
```python
import websocket
import json

class RealTimeSync:
    def __init__(self, erp_url, mes_url):
        self.erp_ws = websocket.WebSocketApp(
            erp_url,
            on_message=self.on_erp_message
        )
        self.mes_ws = websocket.WebSocketApp(
            mes_url,
            on_message=self.on_mes_message
        )
    
    def on_erp_message(self, ws, message):
        data = json.loads(message)
        if data['type'] == 'order_update':
            self.aps.update_order(data['order'])
    
    def on_mes_message(self, ws, message):
        data = json.loads(message)
        if data['type'] == 'execution_update':
            self.aps.update_execution(data['execution'])
```

## IMPLEMENTAÇÃO

### Classes:

1. **ERPConnector** class
   - `import_orders(query_params) -> List[Order]`
   - `export_plan(plan) -> ExportResult`
   - `sync_orders() -> SyncResult`

2. **MESConnector** class
   - `get_execution_status(operation_id) -> ExecutionStatus`
   - `update_execution(execution) -> UpdateResult`
   - `get_machine_status(machine_id) -> MachineStatus`

3. **WebhookManager** class
   - `register_webhook(event_type, url) -> Webhook`
   - `trigger_webhook(event) -> None`
   - `handle_incoming_webhook(request) -> Response`

4. **RealTimeSyncManager** class
   - `connect_erp(url) -> Connection`
   - `connect_mes(url) -> Connection`
   - `handle_realtime_update(update) -> None`

## TESTES
- Testar importação de ordens (validação de dados)
- Verificar exportação de planos (formato correto)
- Testar webhooks (end-to-end)
- Validar sincronização em tempo real (latência < 1s)

## FICHEIRO DE SAÍDA
`backend/integration/advanced_erp_mes_connector.py`
```

---

## 📊 RESUMO DE STATUS E PRIORIDADES

| # | Funcionalidade | Status | Prioridade | Ficheiros a Criar |
|---|---------------|--------|------------|-------------------|
| 1 | Planeamento Encadeado Avançado | ⚠️ Parcial | Alta | `chained_scheduler_advanced.py` |
| 2 | LLM Local com LoRA | ⚠️ Básico | Alta | `lora_trainer.py`, `vector_store.py`, `rag_engine.py` |
| 3 | What-If Conversacional | ⚠️ Básico | Alta | `whatif_advanced.py` |
| 4 | Relatórios Automáticos | ⚠️ Parcial | Média | `llm_report_generator.py` |
| 5 | AutoML Avançado | ⚠️ Parcial | Média | `automl_advanced.py` |
| 6 | Dashboards Avançados | ⚠️ Parcial | Média | `advanced_visualizations.py` |
| 7 | Planeamento Estratégico | ❌ Não existe | Alta | `strategic_planner.py` |
| 8 | Integração ERP/MES | ⚠️ Básico | Média | `advanced_erp_mes_connector.py` |

---

## 🎯 PRÓXIMOS PASSOS

1. **Implementar Planeamento Estratégico** (prioridade máxima - não existe)
2. **Melhorar LLM Local** (adicionar LoRA, vector DB)
3. **Avançar What-If Conversacional** (parser NL avançado)
4. **Completar AutoML** (H2O.ai integration)
5. **Melhorar Dashboards** (visualizações interativas)

---

**Todos os prompts acima são super detalhados, com modelos matemáticos avançados e implementações inovadoras!** 🚀

