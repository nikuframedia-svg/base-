# Painel de KPIs — Estação de Extrusão

Calcula e mostra os KPIs do método de planeamento da extrusão
(ver `METODO_PLANEAMENTO_EXTRUSAO.md`, §7) a partir dos três ficheiros de dados.

## Componentes
- `kpi_engine.py` — lê os 3 ficheiros e calcula os KPIs (só precisa de `openpyxl`).
- `dashboard.py` — gera um dashboard HTML self-contained.
- `../api/extrusion_kpi.py` — endpoints FastAPI.

## KPIs calculados
| KPI | Descrição |
|---|---|
| Output/dia (mediana, máx) | do log da prensa |
| kg/h real (P50, P10–P90) | cadência real por extrusão |
| Produtividade por matriz | kg/h real por matriz (driver de cadência) |
| Trocas de matriz/dia | proxy de tempo de setup |
| Pendente em atraso / futuro | carteira vs. data de entrega |
| OTD % | on-time delivery (requer data fim embalagem na origem) |
| Carga por prensa | planeado vs. pendente vs. capacidade |
| Carga semanal vs. capacidade | utilização futura (pico de risco) |
| Backlog (cobertura) | semanas de trabalho em carteira |
| Matrizes bloqueadas | restrição dura (defeitos) |

## Dados de entrada
Coloque os 3 `.xlsx` numa pasta (por omissão `app/data/extrusion/`):
- `Analysis*.xlsx` — log da prensa
- `Livro1*.xlsx` — carteira de OFs (folha `Folha1`)
- `Extrusion_Overview*.xlsx` — capacidade / backlog / matrizes com problemas

A pasta é configurável via `EXTRUSION_DATA_DIR` ou pelo parâmetro `data_dir`.

## Utilização

### API
```
GET /api/extrusion-kpi/            -> JSON
GET /api/extrusion-kpi/dashboard   -> HTML
GET /api/extrusion-kpi/?data_dir=/caminho/para/dados
```

### CLI
```bash
# JSON
python -m app.extrusion_kpi.kpi_engine /caminho/para/dados

# Dashboard HTML
python -m app.extrusion_kpi.dashboard /caminho/para/dados dashboard.html
```

## Notas
- O OTD aparece como `—` enquanto a carteira não tiver a **data real de fim de
  embalagem** preenchida (lacuna a colmatar na origem dos dados).
- Os parâmetros de capacidade por prensa têm defaults da folha
  *Capacidade Extrusao*; podem ser passados em `ExtrusionKPIConfig`.
