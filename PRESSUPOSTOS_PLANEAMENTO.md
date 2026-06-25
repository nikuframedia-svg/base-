# Pressupostos do Planeamento de Extrusão

Descrição sucinta de **todos os pressupostos** aplicados no motor de KPIs e na
proposta de planeamento (`factory-optimizer/backend/app/extrusion_kpi/`).
Cada ponto indica a origem (dado real vs. assunção) para fácil validação.

---

## 1. Fontes de dados
| Fonte | Ficheiro | Uso |
|---|---|---|
| Log da prensa | `Analysis*.xlsx` (Sheet1) | kg/h real, output, trocas de matriz |
| Carteira de OFs | `Livro1*.xlsx` (folha `Folha1`) | ordens, estados, datas, kg, liga, prensa |
| Capacidade / backlog / matrizes | `Extrusion_Overview*.xlsx` | capacidade, backlog, matrizes bloqueadas |

- **"Hoje"** = última data presente no log da prensa (16-jun-2026) quando não indicado.

## 2. Ordens em aberto
- **Ordem em aberto** = `Kgs Pend.` > 0 (kg ainda por produzir). *(real)*

## 3. Estados (coluna única `Status`, código 00–13)
Fonte única e sempre preenchida; mapeada para nome PT *(definições do cliente)*:
| Código | Significado |
|---|---|
| 00 | Material em stock (colocado manualmente) |
| 01 | Testes / matrizes por aprovar / encomendas em espera |
| 02 | Pré-planeada — **ligas duras** (6063-T81, 6005, 6082) |
| 04 | Pré-planeada |
| 05 / 06 | Planeada |
| 07 | Antes do forno |
| 08 | Matriz no forno |
| 09 | Na prensa |
| 10 | Em execução |
| 11 | Reporte de serra |
| 13 | Embalagem / Reporte |

## 4. Tipo de artigo e lead time a jusante
- **Tipo X** extraído do código `L12345.X.YYY` (penúltimo segmento) do campo
  `_ItemOriginal` — o artigo final do cliente. *(real)*
- **Lead a jusante** (dias de **calendário**) = lead do acabamento **+ 3 dias de embalagem**:

| X | Processo | Lead acabamento | Total a jusante |
|---|---|---|---|
| 0 | Extrusão (bruto) | — (extrusão = **4 d** nominais, modelada pela prensa) | **3 d** |
| 1 | Lacado | 7 | 10 |
| 2 | Lacado efeito madeira | 14 | 17 |
| 3 | Anodizado | 14 | 17 |
| 4 | Anodizado polido | 21 | 24 |
| 5 | Cravado bruto | 7 | 10 |
| 6 | Cravado lacado | 7 | 10 |
| 7 | Maquinado bruto | 7 | 10 |
| 8 | Maquinado tratado | 7 | 10 |
| 9 | Assemblado | 7 *(assumido — valor não fornecido)* | 10 |

- **Tipo 0 (bruto):** a extrusão (4 d nominais) é a própria operação já agendada
  pela capacidade da prensa → não se soma; a jusante fica só a embalagem (+3 d). *(decisão confirmada)*
- **85 OFs sem `_ItemOriginal`** (campo vazio na origem) → tratadas como bruto
  (lead 3 d). 85% delas já passaram na prensa. *(lacuna de dados)*

## 5. Capacidade das prensas
- **Nominal por semana** (folha *Capacidade Extrusão*): P2 110 640 · P3 168 000 ·
  P4 162 000 · P5 114 000 kg. **kg/h:** P2 922 · P3 1 400 · P4 1 350 · P5 950. *(real)*
- **kg/dia** = kg/semana ÷ **5 dias úteis**. *(assunção: 5 dias/semana)*
- **Calendário:** 24 h por dia útil; fins-de-semana excluídos. *(assunção)*

## 6. Produtividade (kg/h)
- **kg/h real por matriz** = Σ kg ÷ Σ duração, do log da prensa. *(real)*
- Estatística de cadência só com extrusões de **duração > 30 s** (remove ruído). *(assunção)*
- Fallback de cadência: kg/h nominal da prensa → mediana global (~1 500). *(assunção)*

## 7. Previsão de conclusão (capacidade-finita)
- Por prensa, OFs ordenadas pela **data de entrega** (mais cedo primeiro). *(regra)*
- Consomem a **capacidade diária** da prensa em dias úteis até cobrir o kg pendente.
- **Data de extrusão prevista** = dia em que o kg fica coberto.
- **Entrega prevista** = extrusão + lead a jusante (§4).
- **Atraso** quando entrega prevista > data de entrega.

## 8. Proposta de planeamento (sequência otimizada)
- **Sequenciação:** EDD (data de entrega) **com campanhas de matriz** — OFs da
  mesma matriz correm consecutivas; a campanha herda a entrega mais cedo das suas OFs. *(otimização de processo)*
- **Tempo de prensa por OF** = kg ÷ kg/h real da matriz. *(real)*
- **Tempo de troca de matriz (setup)** = **0,3 h** por mudança de matriz. *(assunção — afinável)*
- **24 h/dia útil**, dias úteis apenas.
- **Entrega prevista / atraso** como em §7.

## 9. Ligas duras
- **Liga dura** = `Composto Liga` começa por `60638` (6063-T8x), `6005` ou `6082`. *(regra sobre dado real)*
- OFs de liga dura são **marcadas** no plano; a cadência kg/h é mostrada à parte.
- **`hard_alloy_speed_factor` = 1,0** (sem ajuste). O log da prensa **não regista a
  liga**, logo o kg/h por matriz é uma média de todas as ligas — não isola o efeito
  da liga dura. Definir <1 (ex.: 0,7) quando a perda de velocidade real for conhecida. *(limitação de dados)*

## 10. Outros KPIs
- **Trocas de matriz/dia** = nº de mudanças de matriz entre extrusões consecutivas no log. *(real, proxy de setup)*
- **Backlog (cobertura)** = backlog (folha *historico*) ÷ output semanal equivalente. *(real)*
- **OTD %** = `Data Fim Emb.` ≤ `Data Entrega`. Atualmente **indisponível** — o campo
  de fim de embalagem está vazio na carteira. *(lacuna de dados a colmatar na origem)*
- **Matrizes bloqueadas** = folha *Mat c problemas* (restrição dura). *(real)*

---

### Parâmetros afináveis (`ExtrusionKPIConfig`)
`capacity_kg_week`, `capacity_kg_day`, `capacity_kg_h`, `working_days_per_week` (5),
`plan_hours_per_day` (24), `plan_setup_hours` (0,3), `downstream_buffer_days` (3, fallback),
`hard_alloy_speed_factor` (1,0), `today`.

### Pontos em aberto (a confirmar/melhorar com o cliente)
1. **Lead time do tipo 9 (Assemblado)** — assumido 7 d.
2. **Perda de velocidade real das ligas duras** → preencher `hard_alloy_speed_factor`.
3. **Tempo de setup real** — medir do log (intervalos entre matrizes) em vez de 0,3 h fixo.
4. **`_ItemOriginal` vazio em 85 OFs** e **fim de embalagem ausente** (OTD) — corrigir na origem.
