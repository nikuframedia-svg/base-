# Método de Planeamento — Estação de Extrusão de Alumínio

> Documento de método elaborado a partir da análise dos dados históricos de produção e da carteira de encomendas futuras (junho 2026). Liga-se ao motor APS já existente no repositório (`factory-optimizer` / ProdPlan 4.0).

---

## 1. Inventário e leitura dos dados disponíveis

Foram analisados três ficheiros. Cada um cobre uma camada diferente do problema de planeamento.

| Ficheiro | Folha(s) | O que é | Papel no planeamento |
|---|---|---|---|
| `Analysis_15_37_53` | `Sheet1` | **Log real da prensa** (1 linha por extrusão): OF, Matriz, Dia, Hora início/fim, Comprimento do bloco, Nº de blocos, Velocidade, Kg usados | Fonte de **parâmetros reais** (kg/h, velocidade, output diário) e da **produtividade por matriz** |
| `Livro1` / `Extrusion_Overview→Sheet` | `Folha1` / `Sheet` | **Carteira de OFs (Extrusion Planning / ERP)**: status, prensa planeada, data planeada, kg planeado/encomenda/pendente, cliente, matriz, datas de produção e entrega, estado da OF | **Encomendas futuras** + estado de execução — o objeto a planear |
| `Extrusion_Overview` | `Capacidade Extrusao` | Capacidade por prensa (kg/semana, kg/dia, kg/h) e horas/dia por semana | **Restrição de capacidade** |
| | `CargaEncomendas` | Série semanal de **entrada de encomendas** por cliente desde 2023 | **Previsão de procura** |
| | `Lead Time` | Lead-times por tipo de tratamento (Bruto, Lacado, Mecanizado, …) | **Programação para trás** (backward) a partir da data de entrega |
| | `historico` | Snapshot semanal do **backlog** (por planear, por prensa, por estado) desde set-2024 | Tendência de carga vs. capacidade |
| | `Mat c problemas` | Matrizes com defeitos (vincos, lombas, fora de cotas…) | **Disponibilidade de matriz** (restrição dura) |

---

## 2. Diagnóstico quantitativo (dados reais)

### 2.1 Produção real (log da prensa, 04-mai a 16-jun-2026)
- **3 657 extrusões** / 2 639 OFs / **1 234 matrizes distintas** em ~31 dias úteis de produção.
- **Output total ≈ 3 022 t** no período → **≈ 100 t/dia** (mediana 107 t, máx. 124 t).
- **Cadência real por extrusão (kg/h):** mediana **1 778**, média 2 501, intervalo p10–p90 **810–3 301**.
  → Forte dispersão: o kg/h depende fortemente da **matriz** e do diâmetro do lingote. Planear com um único kg/h médio gera erros grandes; deve usar-se **kg/h por matriz/família** (ver §4.2).
- **Velocidade** mediana 25 (intervalo 1–233) — variável-chave a modelar por matriz.

### 2.2 Capacidade nominal (folha Capacidade Extrusao)
| Prensa | kg/h | kg/dia | kg/semana |
|---|---|---|---|
| P2 | 922 | 22 128 | 110 640 |
| P3 | 1 400 | 33 600 | 168 000 |
| P4 | 1 350 | 32 400 | 162 000 |
| P5 | 950 | 22 800 | 114 000 |
| **Total** | | | **≈ 554 640 (555 t/sem)** |

As horas/dia por prensa **variam por semana** (ex.: P4 arranca a 8 h/dia e sobe para 24 h) — a capacidade é um **calendário**, não uma constante.

### 2.3 Carteira futura (carteira de OFs)
- **2 648 linhas de OF.** Kg planeado por prensa: **P4 714 t · P3 698 t · P5 643 t**.
- **Pendente de produzir: 447 t**, das quais:
  - **71 t já com entrega vencida (atraso)** ⚠️
  - 351 t com entrega futura · 25 t sem data de entrega.
- **Carga planeada de extrusão por semana:** W24 **347 t** · W25 **513 t** · W26 192 t.
  → W25 (513 t) está **no limite** da capacidade semanal (555 t) — risco de não cumprir sem nivelamento.

### 2.4 Backlog (snapshot 15-jun-2026)
- Total **2 104 t** (1 362 t sem reservas); distribuído P3 467 t / P4 432 t / P5 463 t.
- 18,5 t classificadas como **"encomendas que não podemos produzir"** e **6 matrizes com defeito** a bloquear ~22 t (Cadiou, José Luis, etc.).
- Em curso: 117 t extrudidas por embalar/CQ → **WIP a jusante** (serra/embalagem) que também condiciona o fecho da OF.

**Conclusões do diagnóstico:**
1. A estação corre **perto do limite** de capacidade em picos semanais → o planeamento tem de **nivelar carga** entre semanas e prensas.
2. Existe **atraso real (71 t)** → é preciso uma regra explícita de **priorização por data de entrega**.
3. A produtividade varia por matriz → os parâmetros de planeamento devem ser **aprendidos do histórico por matriz/família**, não fixos.
4. Restrições não-capacitivas (matriz com defeito, lead-time de acabamento) determinam datas tão ou mais do que a prensa.

---

## 3. Princípio do método

> **Programação para trás (backward), capacidade-finita, por campanhas de matriz, nivelada por prensa e validada contra restrições.**

Quatro decisões em cadeia, por OF:

```
ENCOMENDA → (1) QUANDO extrudir  → (2) EM QUE PRENSA → (3) EM QUE SEQUÊNCIA → (4) VALIDAR
            backward da entrega    afinidade+carga      campanha de matriz     capacidade+matriz+material
```

---

## 4. Camadas do método

### 4.0 Dados de entrada (refresh semanal/diário)
- **Carteira de OFs** (Extrusion Planning) → lista a planear, com kg pendente, prensa sugerida, matriz, datas.
- **Log da prensa** → recalcular parâmetros (kg/h por matriz).
- **Capacidade** → calendário de horas por prensa/semana.
- **Lead-time de tratamento** + **matrizes com problemas** → restrições.

### 4.1 Cálculo da data-âncora (backward scheduling)
Para cada OF:
```
Data_limite_extrusão = Data_entrega
                       − Lead_time_acabamento(X)         (tipo de artigo X, ver tabela abaixo)
                       − 3 dias (embalagem final)
```
Esta data é a **data mais tardia** em que a OF pode entrar na prensa sem falhar a entrega. Ordena toda a carteira por esta data.

**Tipo de artigo e lead time** — derivado do código do artigo final `L12345.X.YYY` (campo `_ItemOriginal`), onde **X** = penúltimo segmento:

| X | Processo | Lead acabamento | + Embalagem | Lead total a jusante |
|---|---|---|---|---|
| 0 | Extrusão (bruto) | — (os 5 d incluem a extrusão) | +3 | **3 d** |
| 1 | Lacado | 7 d | +3 | 10 d |
| 2 | Lacado efeito madeira | 14 d | +3 | 17 d |
| 3 | Anodizado | 14 d | +3 | 17 d |
| 4 | Anodizado polido | 21 d | +3 | **24 d** |
| 5 | Cravado bruto | 7 d | +3 | 10 d |
| 6 | Cravado lacado | 7 d | +3 | 10 d |
| 7 | Maquinado bruto | 7 d | +3 | 10 d |
| 8 | Maquinado tratado | 7 d | +3 | 10 d |
| 9 | Assemblado | (n/d → 7 d) | +3 | 10 d |

> Implementado em `ARTICLE_TYPE` / `_downstream_days` (kpi_engine). A previsão de entrega = fim de extrusão + lead total a jusante (dias de calendário). É isto que torna o atraso por OF realista: um *anodizado polido* tem de ser extrudido **24 dias** antes da data de entrega.

### 4.2 Parâmetros de produtividade (aprendidos do histórico)
Do log da prensa, por **matriz** (e por **família/composto de liga + diâmetro** quando a matriz tem poucos dados):
- `kg/h_p50` e `kg/h_p90` (usar **P90/conservador** para promessas de data, P50 para capacidade esperada);
- velocidade típica e nº de cavidades;
- **tempo de setup/troca de matriz** (estimar do gap entre extrusões consecutivas).

> Isto alinha com os modelos já existentes no repo: `app/ml/cycle_time.py` (regressão quantílica P50/P90) e `app/ml/setup_time.py`. O método aqui é **alimentar esses modelos com a granularidade "matriz"**, que é o driver real de cadência nesta estação.

Tempo de prensa de uma OF:
```
Horas_OF = Kg_pendente / kg_h_matriz(p50)
```

### 4.3 Afetação à prensa
1. **Afinidade matriz↔prensa** a partir do histórico (que prensa costuma correr cada matriz/diâmetro).
2. Se a matriz corre em várias prensas → escolher a que **minimiza o atraso** e **nivela a carga** (a prensa com mais folga na semana-alvo).
3. Respeitar capacidade-finita: somatório de `Horas_OF` por prensa/semana ≤ horas disponíveis no calendário.

### 4.4 Sequenciação por campanhas (dentro de cada prensa/dia)
Minimizar trocas (setup) **sem violar datas**:
- agrupar OFs da **mesma matriz** e do **mesmo diâmetro de lingote** em campanha;
- agrupar por **liga/composto** e **têmpera** para reduzir transições;
- a campanha não pode empurrar nenhuma OF para além da sua data-âncora (§4.1) → trade-off **setup vs. OTD** resolvido a favor da entrega.

> Corresponde à "colagem de famílias" já implementada no `scheduler.py`; aqui a família = (matriz/diâmetro/liga).

### 4.5 Validação de restrições (gates)
Uma OF só é programável se:
- ✅ **Matriz disponível** (não está em `Mat c problemas`); se estiver, a OF fica em fila "bloqueada por matriz" e dispara alerta.
- ✅ **Lingote/liga disponível** (cruzar com stock — módulo SmartInventory/MRP do repo).
- ✅ Capacidade da prensa na semana não excedida.
Caso falhe, a OF não entra no plano "executável" — entra na lista de exceções com a causa.

### 4.6 Nivelamento e fecho
- Distribuir a carga das semanas de pico (ex.: W25=513 t) para semanas adjacentes com folga, respeitando datas-âncora.
- Output esperado por prensa/semana = `min(capacidade, carga afetada)`.
- Produzir **plano executável** (lista ordenada por prensa/dia) + **lista de exceções** (atrasos inevitáveis, matrizes/material em falta).

---

## 5. Priorização (regra de desempate)
Quando a capacidade não chega, sequenciar por:
1. **OFs em atraso** (entrega vencida — hoje 71 t);
2. **Folga de entrega** mais curta (data-âncora mais próxima — *slack* mínimo);
3. **Clientes com planeamento >100%** (lista na folha Lead Time: Lecapitaine, Verandier, Joubert, Mecosun, Cadiou…) e reservas/MTS;
4. Menor custo de setup (campanha) como critério final, **sem** sacrificar 1–3.

---

## 6. Previsão de procura (encomendas futuras ainda não em carteira)
Para planear além da carteira firme, usar a folha `CargaEncomendas` (entrada semanal por cliente desde 2023):
- estimar **taxa de entrada por cliente** (média móvel + sazonalidade mensal);
- separar **MTO** (faz-por-encomenda) de **reservas/stock/sistemas**;
- gerar **carga prevista** por semana futura → reservar capacidade ("placeholder") nas prensas para não comprometer 100% do calendário só com a carteira firme.
- Modelo recomendado: o `app/ml/inventory.py` (Croston/TSB) já trata **procura intermitente**, adequado a clientes com encomendas esporádicas.

---

## 7. KPIs de controlo (fecho do ciclo)
| KPI | Definição | Fonte |
|---|---|---|
| **OTD %** | OFs entregues na data prometida / total | carteira (Data Entrega vs. Data Fim Emb.) |
| **Atraso (kg)** | kg pendente com entrega vencida | hoje **71 t** |
| **Utilização por prensa** | kg produzido / capacidade | log + capacidade |
| **Aderência ao plano** | OFs produzidas na prensa/semana planeada | plano vs. log |
| **kg/h real vs. planeado** | desvio do parâmetro por matriz | log |
| **Nº trocas de matriz/dia** | proxy de setup | log (gaps) |
| **Backlog (semanas de cobertura)** | backlog / output semanal | historico |

Recalcular semanalmente; o desvio realimenta os parâmetros (§4.2) — o método **aprende**.

---

## 8. Integração com o sistema existente (ProdPlan 4.0 / factory-optimizer)
O método mapeia diretamente nos componentes já presentes no repo:

| Etapa do método | Componente existente |
|---|---|
| Ingestão dos .xlsx | `app/etl/loader.py` |
| Parâmetros kg/h P50/P90 por matriz | `app/ml/cycle_time.py` |
| Tempo de troca de matriz | `app/ml/setup_time.py` |
| Afetação + sequenciação capacidade-finita | `app/aps/engine.py` + `app/aps/scheduler.py` (colagem de famílias, overlap) |
| Afetação de prensa alternativa | `app/ml/routing.py` (bandit de rotas) |
| Restrição de material/lingote | módulo SmartInventory / MRP |
| Previsão de procura intermitente | `app/ml/inventory.py` (Croston/TSB) |
| Gargalos e what-if (avaria de prensa, VIP) | `app/api/bottlenecks.py`, `app/api/whatif.py` |
| Explicação das decisões | `app/llm/explanations.py` |

**Adaptações necessárias para a extrusão:**
1. Definir a **"família" = (matriz, diâmetro de lingote, liga/têmpera)** na colagem do scheduler.
2. Granularidade de parâmetros ao nível **matriz** no `cycle_time`.
3. Acrescentar o **gate de matriz com defeito** (`Mat c problemas`) como restrição dura.
4. Calendário de capacidade **variável por semana/prensa** (não constante).

---

## 9. Fluxo operacional semanal (resumo executável)
1. **Atualizar dados** (carteira, log, capacidade, lead-times, matrizes com problemas).
2. **Recalcular parâmetros** kg/h por matriz a partir do log.
3. **Calcular data-âncora** de cada OF (backward da entrega).
4. **Validar gates** (matriz, material, capacidade) → separar executáveis de exceções.
5. **Afetar prensa** (afinidade + nivelamento).
6. **Sequenciar por campanhas** sem furar datas.
7. **Publicar** plano por prensa/dia + lista de exceções + KPIs.
8. **Medir** desvio na semana seguinte e **realimentar** os parâmetros.

---

### Próximos passos sugeridos
- **(A)** Implementar um *script* de prova-de-conceito que lê os 3 ficheiros, calcula kg/h por matriz, datas-âncora e gera o plano nivelado por prensa para as próximas 4 semanas (validável contra W24–W26 reais).
- **(B)** Integrar a "família = matriz/diâmetro/liga" e o gate de matriz no `scheduler.py` existente.
- **(C)** Construir o painel de KPIs (§7) sobre a API atual.

> Indique qual prefere e avanço com a implementação na branch.
