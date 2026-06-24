"""Gerador de dashboard HTML self-contained dos KPIs de extrusão.

Recebe o dicionário devolvido por ``compute_kpis`` e produz um HTML único
(sem dependências externas) que pode ser aberto no browser ou servido pela API.
"""

from __future__ import annotations

import html
from typing import Any, Dict, Optional


def _fmt(v: Optional[float], unit: str = "") -> str:
    if v is None:
        return "—"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, (int, float)):
        s = f"{v:,.0f}".replace(",", " ") if abs(v) >= 1000 else f"{v}"
        return f"{s}{unit}"
    return html.escape(str(v))


def _card(title: str, value: str, sub: str = "", tone: str = "") -> str:
    cls = f"card {tone}".strip()
    return (
        f'<div class="{cls}"><div class="card-t">{html.escape(title)}</div>'
        f'<div class="card-v">{value}</div>'
        f'<div class="card-s">{html.escape(sub)}</div></div>'
    )


def _bar(pct: Optional[float]) -> str:
    if pct is None:
        return ""
    tone = "ok" if pct < 80 else ("warn" if pct < 95 else "bad")
    width = min(100.0, pct)
    return f'<div class="bar"><div class="bar-f {tone}" style="width:{width:.0f}%"></div></div>'


def render_dashboard(data: Dict[str, Any]) -> str:
    k = data.get("kpis", {})
    prod = k.get("production", {})
    deliv = k.get("delivery", {})
    cap = k.get("capacity", {})
    backlog = k.get("backlog", {})
    blocked = k.get("blocked_dies", {})
    src = data.get("sources", {})

    # --- KPI cards principais ---
    late = deliv.get("late_kg")
    late_tone = "bad" if late and late > 0 else "ok"
    util_weeks = k.get("weekly_load_vs_capacity", [])
    peak = max((w["utilization_pct"] or 0 for w in util_weeks), default=0)
    peak_tone = "ok" if peak < 80 else ("warn" if peak < 95 else "bad")
    openo = k.get("open_orders", {})
    fc = k.get("completion_forecast", {})
    fc_late = fc.get("forecast_late_orders")

    cards = "".join([
        _card("Ordens em aberto", _fmt(openo.get("count")),
              f"{_fmt(openo.get('kg'))} kg pendentes"),
        _card("Conclusão da estação", _fmt(fc.get("station_clear_date")),
              "data prevista p/ extrudir tudo o que está em aberto"),
        _card("OFs com risco de atraso", _fmt(fc_late),
              f"{_fmt(fc.get('forecast_late_kg'))} kg (previsão > entrega)",
              "bad" if fc_late else "ok"),
        _card("Output / dia (mediana)", _fmt(prod.get("kg_per_day_median"), " kg"),
              f"máx {_fmt(prod.get('kg_per_day_max'))} kg"),
        _card("kg/h real (P50)", _fmt(prod.get("real_kg_h_p50")),
              f"P10–P90: {_fmt(prod.get('real_kg_h_p10'))}–{_fmt(prod.get('real_kg_h_p90'))}"),
        _card("Pendente em atraso", _fmt(late, " kg"),
              "entrega já vencida", late_tone),
        _card("Backlog (cobertura)", _fmt(backlog.get("coverage_weeks"), " sem"),
              f"{_fmt(backlog.get('total_sem_reservas'))} kg s/ reservas"),
        _card("Pico utilização semanal", _fmt(peak, "%"),
              "carga futura vs. capacidade", peak_tone),
        _card("Trocas de matriz / dia", _fmt(k.get("die_changeovers_per_day_avg")),
              "proxy de setup"),
        _card("Matrizes bloqueadas", _fmt(blocked.get("count")),
              f"{_fmt(blocked.get('blocked_kg'))} kg parados", "warn" if blocked.get("count") else ""),
    ])

    # --- Tabela: ordens em aberto por estado ---
    open_rows = "".join(
        f"<tr><td>{html.escape(str(s['state']))}</td>"
        f"<td class='num'>{_fmt(s['orders'])}</td>"
        f"<td class='num'>{_fmt(s['kg'])}</td></tr>"
        for s in (openo.get("by_state") or [])
    ) or "<tr><td colspan=3>Sem dados</td></tr>"

    # --- Tabela: previsão de conclusão por prensa ---
    fc_press_rows = "".join(
        f"<tr><td>{html.escape(str(p))}</td>"
        f"<td class='num'>{_fmt(v['orders'])}</td>"
        f"<td class='num'>{_fmt(v['pending_kg'])}</td>"
        f"<td class='num'>{_fmt(v['kg_day'])}</td>"
        f"<td class='num'>{_fmt(v['working_days'])}</td>"
        f"<td>{html.escape(str(v['clear_date'] or '—'))}</td></tr>"
        for p, v in (fc.get("by_press") or {}).items()
    ) or "<tr><td colspan=6>Sem dados</td></tr>"

    # --- Tabela: OFs em risco de atraso (top) ---
    risk_rows = "".join(
        f"<tr><td>{html.escape(str(o.get('of') or '—'))}</td>"
        f"<td>{html.escape(str(o['die']))}</td>"
        f"<td>{html.escape(str(o.get('customer') or ''))}</td>"
        f"<td>{html.escape(str(o['press']))}</td>"
        f"<td class='num'>{_fmt(o['kg_pending'])}</td>"
        f"<td>{html.escape(str(o['due_date'] or '—'))}</td>"
        f"<td>{html.escape(str(o['extrusion_eta'] or '—'))}</td>"
        f"<td class='bad-t'>{html.escape(str(o['delivery_eta'] or '—'))}</td></tr>"
        for o in (fc.get("risk_orders_top") or [])
    ) or "<tr><td colspan=8>Nenhuma OF em risco</td></tr>"

    # --- Tabela: carga semanal vs capacidade ---
    week_rows = "".join(
        f"<tr><td>{html.escape(w['week'])}</td>"
        f"<td class='num'>{_fmt(w['planned_kg'])}</td>"
        f"<td class='num'>{_fmt(w['capacity_kg'])}</td>"
        f"<td class='num'>{_fmt(w['utilization_pct'], '%')}</td>"
        f"<td>{_bar(w['utilization_pct'])}</td></tr>"
        for w in util_weeks
    ) or "<tr><td colspan=5>Sem dados</td></tr>"

    # --- Tabela: carga por prensa ---
    press_rows = ""
    for p, v in (k.get("load_by_press") or {}).items():
        cap_w = (cap.get("kg_week_by_press") or {}).get(p)
        press_rows += (
            f"<tr><td>{html.escape(p)}</td>"
            f"<td class='num'>{_fmt(v['planned_kg'])}</td>"
            f"<td class='num'>{_fmt(v['pending_kg'])}</td>"
            f"<td class='num'>{_fmt(cap_w)}</td></tr>"
        )
    press_rows = press_rows or "<tr><td colspan=4>Sem dados</td></tr>"

    # --- Tabela: produtividade por matriz (top) ---
    die_rows = "".join(
        f"<tr><td>{html.escape(d['die'])}</td>"
        f"<td class='num'>{_fmt(d['kg'])}</td>"
        f"<td class='num'>{_fmt(d['kg_h'])}</td></tr>"
        for d in (k.get("die_productivity_top") or [])
    ) or "<tr><td colspan=3>Sem dados</td></tr>"

    # --- Tabela: matrizes bloqueadas ---
    blk_rows = "".join(
        f"<tr><td>{html.escape(str(d['die']))}</td>"
        f"<td class='num'>{_fmt(d.get('kg'))}</td>"
        f"<td>{html.escape(str(d.get('customer') or ''))}</td>"
        f"<td>{html.escape(str(d.get('defect') or ''))}</td></tr>"
        for d in (blocked.get("items") or [])
    ) or "<tr><td colspan=4>Nenhuma</td></tr>"

    otd = deliv.get("otd_pct")
    otd_note = (
        f"OTD: <b>{_fmt(otd, '%')}</b> (amostra {deliv.get('otd_sample')})"
        if otd is not None else
        "OTD: <b>—</b> (sem data real de fim de embalagem na carteira — lacuna de dados a colmatar na origem)"
    )

    return _TEMPLATE.format(
        generated=html.escape(str(data.get("generated_at", ""))),
        src_log=html.escape(str(src.get("production_log") or "—")),
        src_order=html.escape(str(src.get("order_book") or "—")),
        src_over=html.escape(str(src.get("overview") or "—")),
        period=f"{prod.get('period_start','?')} → {prod.get('period_end','?')}",
        runs=_fmt(prod.get("runs")),
        dies=_fmt(prod.get("distinct_dies")),
        total_kg=_fmt(prod.get("total_kg")),
        cards=cards,
        week_rows=week_rows,
        press_rows=press_rows,
        die_rows=die_rows,
        blk_rows=blk_rows,
        open_rows=open_rows,
        fc_press_rows=fc_press_rows,
        risk_rows=risk_rows,
        station_clear=html.escape(str(fc.get("station_clear_date") or "—")),
        buffer_days=_fmt(fc.get("buffer_days")),
        otd_note=otd_note,
        total_cap=_fmt(cap.get("total_kg_week")),
    )


_TEMPLATE = """<!DOCTYPE html>
<html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel KPIs — Extrusão</title>
<style>
  :root {{ --bg:#0B0B0B; --card:#161616; --card2:#121212; --pri:#00E676; --txt:#EDEDED; --mut:#9AA0A6;
          --warn:#FFB300; --bad:#FF5252; --ok:#00E676; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--txt); font-family:Inter,system-ui,Arial,sans-serif; padding:24px; }}
  h1 {{ font-size:24px; margin:0 0 4px; }}
  h2 {{ font-size:18px; margin:28px 0 12px; }}
  .sub {{ color:var(--mut); font-size:13px; margin-bottom:8px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px; margin-top:16px; }}
  .card {{ background:var(--card); border-radius:16px; padding:16px 18px; border:1px solid #222; }}
  .card.bad {{ border-color:rgba(255,82,82,.5); }}
  .card.warn {{ border-color:rgba(255,179,0,.5); }}
  .card-t {{ color:var(--mut); font-size:13px; }}
  .card-v {{ font-size:28px; font-weight:600; margin:6px 0 2px; }}
  .card.bad .card-v {{ color:var(--bad); }}
  .card.warn .card-v {{ color:var(--warn); }}
  .card-s {{ color:var(--mut); font-size:12px; }}
  table {{ width:100%; border-collapse:collapse; background:var(--card2); border-radius:12px; overflow:hidden; }}
  th, td {{ text-align:left; padding:10px 12px; font-size:14px; border-bottom:1px solid #1e1e1e; }}
  th {{ color:var(--mut); font-weight:500; background:#181818; position:sticky; top:0; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.bad-t {{ color:var(--bad); font-weight:500; }}
  tr:last-child td {{ border-bottom:none; }}
  .bar {{ background:#222; border-radius:6px; height:10px; width:120px; }}
  .bar-f {{ height:10px; border-radius:6px; }}
  .bar-f.ok {{ background:var(--ok); }} .bar-f.warn {{ background:var(--warn); }} .bar-f.bad {{ background:var(--bad); }}
  .two {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
  @media (max-width:900px) {{ .two {{ grid-template-columns:1fr; }} }}
  .foot {{ color:var(--mut); font-size:12px; margin-top:32px; border-top:1px solid #222; padding-top:12px; }}
  .pill {{ display:inline-block; background:#181818; border:1px solid #222; border-radius:999px; padding:3px 10px; font-size:12px; color:var(--mut); margin-right:6px; }}
</style></head>
<body>
  <h1>Painel de KPIs — Estação de Extrusão</h1>
  <div class="sub">Gerado em {generated} · Período de produção {period}</div>
  <div>
    <span class="pill">Log: {src_log}</span>
    <span class="pill">Carteira: {src_order}</span>
    <span class="pill">Overview: {src_over}</span>
    <span class="pill">{runs} extrusões · {dies} matrizes · {total_kg} kg</span>
  </div>

  <div class="grid">{cards}</div>

  <div class="two">
    <div>
      <h2>Carga futura vs. capacidade ({total_cap} kg/sem)</h2>
      <table><thead><tr><th>Semana</th><th class="num">Planeado</th><th class="num">Capacidade</th><th class="num">Util.</th><th></th></tr></thead>
      <tbody>{week_rows}</tbody></table>
    </div>
    <div>
      <h2>Carga por prensa (kg)</h2>
      <table><thead><tr><th>Prensa</th><th class="num">Planeado</th><th class="num">Pendente</th><th class="num">Cap./sem</th></tr></thead>
      <tbody>{press_rows}</tbody></table>
    </div>
  </div>

  <div class="two">
    <div>
      <h2>Ordens em aberto por estado</h2>
      <table><thead><tr><th>Estado</th><th class="num">OFs</th><th class="num">kg pendente</th></tr></thead>
      <tbody>{open_rows}</tbody></table>
    </div>
    <div>
      <h2>Previsão de conclusão por prensa</h2>
      <table><thead><tr><th>Prensa</th><th class="num">OFs</th><th class="num">kg pend.</th><th class="num">kg/dia</th><th class="num">dias úteis</th><th>Conclui em</th></tr></thead>
      <tbody>{fc_press_rows}</tbody></table>
      <div class="sub" style="margin-top:8px">Estação conclui o aberto em <b>{station_clear}</b>. Previsão de entrega = extrusão + {buffer_days} dias úteis (serra+embalagem+tratamento).</div>
    </div>
  </div>

  <h2>OFs com risco de atraso (previsão de entrega &gt; data de entrega)</h2>
  <table><thead><tr><th>OF</th><th>Matriz</th><th>Cliente</th><th>Prensa</th><th class="num">kg pend.</th><th>Entrega</th><th>Extrusão (prev.)</th><th>Entrega (prev.)</th></tr></thead>
  <tbody>{risk_rows}</tbody></table>

  <div class="two">
    <div>
      <h2>Produtividade real por matriz (top volume)</h2>
      <table><thead><tr><th>Matriz</th><th class="num">kg período</th><th class="num">kg/h real</th></tr></thead>
      <tbody>{die_rows}</tbody></table>
    </div>
    <div>
      <h2>Matrizes bloqueadas (restrição dura)</h2>
      <table><thead><tr><th>Matriz</th><th class="num">kg</th><th>Cliente</th><th>Defeito</th></tr></thead>
      <tbody>{blk_rows}</tbody></table>
    </div>
  </div>

  <div class="foot">{otd_note}<br>
  Método: ver METODO_PLANEAMENTO_EXTRUSAO.md (§7 KPIs). Verde &lt;80% · Amarelo 80–95% · Vermelho &gt;95% de utilização.</div>
</body></html>"""


if __name__ == "__main__":  # pragma: no cover
    import sys
    from .kpi_engine import compute_kpis, ExtrusionKPIConfig

    cfg = ExtrusionKPIConfig()
    if len(sys.argv) > 1:
        cfg.data_dir = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "extrusion_kpi_dashboard.html"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render_dashboard(compute_kpis(cfg)))
    print(f"Dashboard escrito em {out}")
