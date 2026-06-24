"""KPIs de planeamento da estação de extrusão de alumínio.

Lê os três ficheiros de dados da estação e calcula os KPIs definidos no
método de planeamento (METODO_PLANEAMENTO_EXTRUSAO.md, §7):

- OTD % (on-time delivery)
- Atraso (kg pendente com entrega vencida)
- Utilização por prensa
- kg/h real vs. planeado
- Nº de trocas de matriz / dia
- Backlog (semanas de cobertura)
- Carga futura por semana vs. capacidade
"""

from .kpi_engine import compute_kpis, ExtrusionKPIConfig

__all__ = ["compute_kpis", "ExtrusionKPIConfig"]
