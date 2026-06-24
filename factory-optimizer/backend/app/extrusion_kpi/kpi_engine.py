"""Motor de cálculo dos KPIs da estação de extrusão.

Dependências: apenas ``openpyxl`` + biblioteca-padrão (sem pandas), para
poder correr de forma isolada e barata.

Fontes de dados (3 ficheiros):
  1. Log da prensa            -> 1 linha por extrusão (OF, Matriz, Dia, horas, Kg)
  2. Carteira de OFs           -> Extrusion Planning / ERP (status, prensa, kgs, datas)
  3. Overview                  -> Capacidade, historico (backlog), Mat c problemas

Os caminhos são configuráveis (ver ``ExtrusionKPIConfig``); por omissão
procuram-se em ``<backend>/app/data/extrusion``.
"""

from __future__ import annotations

import os
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, List, Optional

import openpyxl


# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------

_DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "extrusion"
)

# Capacidade nominal por prensa (folha "Capacidade Extrusao").
DEFAULT_CAPACITY_KG_WEEK = {"P2": 110640, "P3": 168000, "P4": 162000, "P5": 114000}
DEFAULT_CAPACITY_KG_H = {"P2": 922, "P3": 1400, "P4": 1350, "P5": 950}


@dataclass
class ExtrusionKPIConfig:
    """Localização dos ficheiros e parâmetros de cálculo."""

    data_dir: str = _DEFAULT_DATA_DIR
    production_log: Optional[str] = None       # Analysis_*.xlsx
    order_book: Optional[str] = None           # Livro1.xlsx (Folha1) ou Overview->Sheet
    order_book_sheet: str = "Folha1"
    overview: Optional[str] = None             # Extrusion_Overview.xlsx
    today: Optional[datetime] = None           # "agora" para cálculo de atraso
    capacity_kg_week: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_CAPACITY_KG_WEEK))
    capacity_kg_h: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_CAPACITY_KG_H))
    # Capacidade diária por prensa (kg/dia útil). Se None, deriva de kg_week/5.
    capacity_kg_day: Optional[Dict[str, float]] = None
    # Buffer a jusante (serra + embalagem + tratamento) em dias úteis, da
    # data de extrusão até à entrega — usado na previsão de cumprimento.
    downstream_buffer_days: int = 3
    working_days_per_week: int = 5

    def resolve(self) -> "ExtrusionKPIConfig":
        """Preenche caminhos em falta procurando por padrão no data_dir."""
        if self.production_log is None:
            self.production_log = _find(self.data_dir, ("analysis", "analysis_"))
        if self.order_book is None:
            self.order_book = _find(self.data_dir, ("livro1", "livro"))
        if self.overview is None:
            self.overview = _find(self.data_dir, ("extrusion_overview", "overview"))
        if self.capacity_kg_day is None:
            wd = self.working_days_per_week or 5
            self.capacity_kg_day = {p: round(kw / wd) for p, kw in self.capacity_kg_week.items()}
        return self


def _find(folder: str, name_starts: tuple) -> Optional[str]:
    if not folder or not os.path.isdir(folder):
        return None
    for fn in sorted(os.listdir(folder)):
        low = fn.lower()
        if low.endswith(".xlsx") and any(low.startswith(p) or p in low for p in name_starts):
            return os.path.join(folder, fn)
    return None


# --------------------------------------------------------------------------
# Helpers de parsing
# --------------------------------------------------------------------------

def _as_date(v: Any) -> Optional[datetime]:
    if isinstance(v, datetime):
        return v if v.year > 2000 else None
    if isinstance(v, str):
        v = v.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                d = datetime.strptime(v, fmt)
                return d if d.year > 2000 else None
            except ValueError:
                continue
    return None


def _as_float(v: Any) -> Optional[float]:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        v = v.replace(",", ".").strip()
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _duration_seconds(start: Any, end: Any) -> Optional[float]:
    def parse(t):
        if not isinstance(t, str):
            return None
        try:
            return datetime.strptime(t.split(".")[0], "%H:%M:%S")
        except ValueError:
            return None
    s, e = parse(start), parse(end)
    if not s or not e:
        return None
    sec = (e - s).total_seconds()
    if sec < 0:
        sec += 86400  # passou a meia-noite
    return sec if sec > 0 else None


# --------------------------------------------------------------------------
# Leitura das fontes
# --------------------------------------------------------------------------

def _read_production_log(path: str) -> List[Dict[str, Any]]:
    """Lê o log da prensa. Cabeçalho na linha 10, dados a partir da 11."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Sheet1"] if "Sheet1" in wb.sheetnames else wb.worksheets[0]
    runs: List[Dict[str, Any]] = []
    for r in ws.iter_rows(min_row=11, values_only=True):
        po = r[0]
        if po is None or (isinstance(po, str) and po.startswith("Report created")):
            continue
        kg = _as_float(r[8]) or 0.0
        runs.append({
            "po": po,
            "die": r[1],
            "date": _as_date(r[2]),
            "dur_s": _duration_seconds(r[3], r[4]),
            "nbr_block": _as_float(r[6]),
            "speed": _as_float(r[7]),
            "kg": kg,
        })
    wb.close()
    return runs


# Mapeamento dos nomes de coluna da carteira de OFs -> chave interna.
_ORDER_COLS = {
    "Status": "status",
    "Prensa Plan": "press",
    "Kgs Planeado": "kg_planned",
    "Kgs Encomenda": "kg_order",
    "Kgs Pend.": "kg_pending",
    "Kgs Produzido OF": "kg_produced",
    "Matriz": "die",
    "Nome Cliente": "customer",
    "Nr. Cliente": "customer_nr",
    "Data Entrega": "due_date",
    "Data Fim Emb.": "pack_end_date",
    "Data de Extrusão Planeada": "planned_extrusion_date",
    "Status Planeamento Descrição": "plan_status",
    "Estado OF": "of_state",
}


def _read_order_book(path: str, sheet: str) -> List[Dict[str, Any]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet] if sheet in wb.sheetnames else wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    idx = {h: i for i, h in enumerate(header) if h}
    col = {key: idx[name] for name, key in _ORDER_COLS.items() if name in idx}

    def get(r, key, default=None):
        i = col.get(key)
        return r[i] if (i is not None and i < len(r)) else default

    orders: List[Dict[str, Any]] = []
    for r in rows:
        if not r or r[0] is None:
            continue
        orders.append({
            "status": get(r, "status"),
            "press": get(r, "press"),
            "kg_planned": _as_float(get(r, "kg_planned")) or 0.0,
            "kg_order": _as_float(get(r, "kg_order")) or 0.0,
            "kg_pending": _as_float(get(r, "kg_pending")) or 0.0,
            "die": get(r, "die"),
            "customer": get(r, "customer") or get(r, "customer_nr"),
            "due_date": _as_date(get(r, "due_date")),
            "pack_end_date": _as_date(get(r, "pack_end_date")),
            "planned_extrusion_date": _as_date(get(r, "planned_extrusion_date")),
            "plan_status": get(r, "plan_status"),
            "of_state": get(r, "of_state"),
        })
    wb.close()
    return orders


def _read_overview(path: str) -> Dict[str, Any]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out: Dict[str, Any] = {"backlog": None, "dies_with_problems": []}

    # historico -> último snapshot de backlog
    if "historico" in wb.sheetnames:
        ws = wb["historico"]
        last = None
        for r in ws.iter_rows(min_row=3, values_only=True):
            if isinstance(r[0], datetime) and r[5]:  # col5 = TOTAL (sem reservas)
                last = r
        if last:
            out["backlog"] = {
                "date": last[0].isoformat(),
                "por_planear": _as_float(last[1]),
                "P3": _as_float(last[2]),
                "P4": _as_float(last[3]),
                "P5": _as_float(last[4]),
                "total_sem_reservas": _as_float(last[5]),
                "total": _as_float(last[10]) if len(last) > 10 else None,
            }

    # Mat c problemas -> matrizes bloqueadas
    if "Mat c problemas" in wb.sheetnames:
        ws = wb["Mat c problemas"]
        for r in ws.iter_rows(min_row=12, max_row=40, values_only=True):
            die = r[0] if r else None
            if isinstance(die, str) and die and die[0].isalpha() and len(die) >= 4:
                out["dies_with_problems"].append({
                    "die": die,
                    "kg": _as_float(r[1]) if len(r) > 1 else None,
                    "customer": r[2] if len(r) > 2 else None,
                    "defect": r[4] if len(r) > 4 else None,
                })
    wb.close()
    return out


# --------------------------------------------------------------------------
# Previsão de conclusão (simulação de capacidade-finita por prensa)
# --------------------------------------------------------------------------

from datetime import timedelta


def _next_working_day(d: datetime) -> datetime:
    while d.weekday() >= 5:  # 5=sáb, 6=dom
        d += timedelta(days=1)
    return d


def _add_working_days(d: datetime, n: int) -> datetime:
    d = _next_working_day(d)
    for _ in range(n):
        d = _next_working_day(d + timedelta(days=1))
    return d


_FAR = datetime(2999, 1, 1)


def compute_completion_forecast(
    open_orders: List[Dict[str, Any]],
    cfg: "ExtrusionKPIConfig",
    today: datetime,
) -> Dict[str, Any]:
    """Estima a data de extrusão de cada OF em aberto e o cumprimento da entrega.

    Modelo: por prensa, as OFs são sequenciadas pela data-âncora (entrega
    primeiro) e consomem a capacidade diária da prensa em dias úteis. A data
    de extrusão de cada OF é o dia em que a sua quantidade pendente fica
    coberta. A previsão de entrega = extrusão + buffer a jusante.
    """
    cap_day = cfg.capacity_kg_day or {}
    buffer_days = cfg.downstream_buffer_days

    by_press: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
    for o in open_orders:
        by_press[o.get("press")].append(o)

    press_summary: Dict[str, Any] = {}
    order_etas: List[Dict[str, Any]] = []

    for press, lst in by_press.items():
        # prioridade: data de entrega (âncora) ascendente, depois maior pendente
        lst.sort(key=lambda o: (o["due_date"] or _FAR, -o["kg_pending"]))
        total = sum(o["kg_pending"] for o in lst)
        kgday = cap_day.get(press)

        if not kgday:
            press_summary[str(press)] = {
                "pending_kg": round(total), "kg_day": None,
                "clear_date": None, "working_days": None, "orders": len(lst),
            }
            for o in lst:
                order_etas.append(_eta_record(o, None, None, None))
            continue

        cur = _next_working_day(today)
        cap_left = float(kgday)
        for o in lst:
            need = o["kg_pending"]
            while need > 0:
                if cap_left <= 1e-9:
                    cur = _next_working_day(cur + timedelta(days=1))
                    cap_left = float(kgday)
                take = min(need, cap_left)
                need -= take
                cap_left -= take
            ext_eta = cur
            deliv_eta = _add_working_days(ext_eta, buffer_days)
            late = bool(o["due_date"]) and deliv_eta.date() > o["due_date"].date()
            order_etas.append(_eta_record(o, ext_eta, deliv_eta, late))

        import math
        press_summary[str(press)] = {
            "pending_kg": round(total),
            "kg_day": round(kgday),
            "clear_date": cur.date().isoformat(),
            "working_days": math.ceil(total / kgday),
            "orders": len(lst),
        }

    clear_dates = [v["clear_date"] for v in press_summary.values() if v["clear_date"]]
    forecast_late = sum(1 for e in order_etas if e["forecast_late"])
    forecast_late_kg = round(sum(e["kg_pending"] for e in order_etas if e["forecast_late"]))

    # OFs com previsão de entrega mais tardia / em risco (para listagem)
    risk = sorted(
        [e for e in order_etas if e["forecast_late"]],
        key=lambda e: (e["due_date"] or "9999", -e["kg_pending"]),
    )

    return {
        "by_press": press_summary,
        "station_clear_date": max(clear_dates) if clear_dates else None,
        "open_orders": len(open_orders),
        "open_kg": round(sum(o["kg_pending"] for o in open_orders)),
        "forecast_late_orders": forecast_late,
        "forecast_late_kg": forecast_late_kg,
        "buffer_days": buffer_days,
        "risk_orders_top": risk[:20],
    }


def _eta_record(o, ext_eta, deliv_eta, late) -> Dict[str, Any]:
    return {
        "die": o.get("die"),
        "customer": o.get("customer"),
        "press": o.get("press"),
        "kg_pending": round(o["kg_pending"]),
        "due_date": o["due_date"].date().isoformat() if o.get("due_date") else None,
        "extrusion_eta": ext_eta.date().isoformat() if ext_eta else None,
        "delivery_eta": deliv_eta.date().isoformat() if deliv_eta else None,
        "forecast_late": bool(late),
    }


# --------------------------------------------------------------------------
# Cálculo dos KPIs
# --------------------------------------------------------------------------

def _pct(n: float, d: float) -> Optional[float]:
    return round(100.0 * n / d, 1) if d else None


def compute_kpis(config: Optional[ExtrusionKPIConfig] = None) -> Dict[str, Any]:
    """Lê as fontes e devolve o dicionário de KPIs (serializável em JSON)."""
    cfg = (config or ExtrusionKPIConfig()).resolve()

    runs = _read_production_log(cfg.production_log) if cfg.production_log else []
    orders = _read_order_book(cfg.order_book, cfg.order_book_sheet) if cfg.order_book else []
    overview = _read_overview(cfg.overview) if cfg.overview else {}

    today = cfg.today
    if today is None and runs:
        dates = [r["date"] for r in runs if r["date"]]
        today = max(dates) if dates else datetime(2026, 6, 16)
    today = today or datetime(2026, 6, 16)

    result: Dict[str, Any] = {
        "generated_at": today.isoformat(),
        "sources": {
            "production_log": os.path.basename(cfg.production_log) if cfg.production_log else None,
            "order_book": os.path.basename(cfg.order_book) if cfg.order_book else None,
            "overview": os.path.basename(cfg.overview) if cfg.overview else None,
        },
        "kpis": {},
    }
    K = result["kpis"]

    # --- Produção: output, período, kg/h real ---
    if runs:
        kgs = [r["kg"] for r in runs if r["kg"]]
        dates = sorted({r["date"].date() for r in runs if r["date"]})
        day_kg: Dict[Any, float] = defaultdict(float)
        for r in runs:
            if r["date"]:
                day_kg[r["date"].date()] += r["kg"]
        rates = [r["kg"] / (r["dur_s"] / 3600) for r in runs if r["dur_s"] and r["dur_s"] > 30 and r["kg"]]
        rates.sort()
        n_days = len(dates)
        weekly_output = (sum(kgs) / n_days * 5) if n_days else 0  # 5 dias/semana equivalentes

        K["production"] = {
            "runs": len(runs),
            "distinct_dies": len({r["die"] for r in runs if r["die"]}),
            "period_start": dates[0].isoformat() if dates else None,
            "period_end": dates[-1].isoformat() if dates else None,
            "total_kg": round(sum(kgs)),
            "kg_per_day_median": round(statistics.median(day_kg.values())) if day_kg else None,
            "kg_per_day_max": round(max(day_kg.values())) if day_kg else None,
            "real_kg_h_p50": round(statistics.median(rates)) if rates else None,
            "real_kg_h_mean": round(statistics.mean(rates)) if rates else None,
            "real_kg_h_p10": round(rates[len(rates) // 10]) if rates else None,
            "real_kg_h_p90": round(rates[len(rates) * 9 // 10]) if rates else None,
            "equivalent_weekly_output_kg": round(weekly_output),
        }

        # --- kg/h real por matriz (top por volume) — driver de cadência ---
        die_kg: Dict[str, float] = defaultdict(float)
        die_h: Dict[str, float] = defaultdict(float)
        for r in runs:
            if r["die"] and r["dur_s"] and r["kg"]:
                die_kg[r["die"]] += r["kg"]
                die_h[r["die"]] += r["dur_s"] / 3600
        die_rate = [
            {"die": d, "kg": round(die_kg[d]), "kg_h": round(die_kg[d] / die_h[d])}
            for d in die_kg if die_h[d] > 0
        ]
        die_rate.sort(key=lambda x: -x["kg"])
        K["die_productivity_top"] = die_rate[:15]

        # --- Nº de trocas de matriz por dia ---
        by_day_runs: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
        for r in runs:
            if r["date"]:
                by_day_runs[r["date"].date()].append(r)
        changeovers = []
        for day, day_runs in by_day_runs.items():
            seq = [x["die"] for x in day_runs if x["die"]]
            ch = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
            changeovers.append(ch)
        K["die_changeovers_per_day_avg"] = round(statistics.mean(changeovers), 1) if changeovers else None

    # --- Carteira: atraso, OTD, carga futura, utilização planeada ---
    if orders:
        total_pending = sum(o["kg_pending"] for o in orders if o["kg_pending"] > 0)
        late_kg = future_kg = noplan_kg = 0.0
        for o in orders:
            kp = o["kg_pending"]
            if kp <= 0:
                continue
            if o["due_date"]:
                if o["due_date"] < today:
                    late_kg += kp
                else:
                    future_kg += kp
            else:
                noplan_kg += kp

        # OTD: das OFs já embaladas com data de entrega e data fim emb.
        otd_on = otd_total = 0
        for o in orders:
            if o["pack_end_date"] and o["due_date"]:
                otd_total += 1
                if o["pack_end_date"] <= o["due_date"]:
                    otd_on += 1

        K["delivery"] = {
            "total_pending_kg": round(total_pending),
            "late_kg": round(late_kg),
            "future_kg": round(future_kg),
            "no_due_date_kg": round(noplan_kg),
            "otd_pct": _pct(otd_on, otd_total),
            "otd_sample": otd_total,
        }

        # --- Ordens em aberto (kg pendente > 0) ---
        open_orders = [o for o in orders if o["kg_pending"] > 0]
        by_state: Dict[str, List[float]] = defaultdict(lambda: [0, 0.0])
        for o in open_orders:
            st = o["plan_status"] or o["status"] or "(sem estado)"
            by_state[str(st)][0] += 1
            by_state[str(st)][1] += o["kg_pending"]
        K["open_orders"] = {
            "count": len(open_orders),
            "kg": round(sum(o["kg_pending"] for o in open_orders)),
            "by_state": [
                {"state": s, "orders": int(v[0]), "kg": round(v[1])}
                for s, v in sorted(by_state.items(), key=lambda kv: -kv[1][1])
            ],
        }

        # --- Previsão de conclusão (capacidade-finita por prensa) ---
        K["completion_forecast"] = compute_completion_forecast(open_orders, cfg, today)

        # Carga planeada por prensa
        load_press: Dict[str, float] = defaultdict(float)
        pend_press: Dict[str, float] = defaultdict(float)
        for o in orders:
            if o["press"]:
                load_press[o["press"]] += o["kg_planned"]
                if o["kg_pending"] > 0:
                    pend_press[o["press"]] += o["kg_pending"]
        K["load_by_press"] = {
            p: {"planned_kg": round(load_press[p]), "pending_kg": round(pend_press[p])}
            for p in sorted(load_press)
        }

        # Carga futura por semana de extrusão vs capacidade total
        week_load: Dict[str, float] = defaultdict(float)
        for o in orders:
            d = o["planned_extrusion_date"]
            if d:
                iso = d.isocalendar()
                week_load[f"{iso[0]}-W{iso[1]:02d}"] += o["kg_planned"]
        total_week_cap = sum(cfg.capacity_kg_week.values())
        future_weeks = sorted(w for w in week_load if w >= today.strftime("%Y-W%V"))
        K["weekly_load_vs_capacity"] = [
            {
                "week": w,
                "planned_kg": round(week_load[w]),
                "capacity_kg": total_week_cap,
                "utilization_pct": _pct(week_load[w], total_week_cap),
            }
            for w in future_weeks[:8]
        ]

    # --- Capacidade configurada ---
    K["capacity"] = {
        "kg_week_by_press": cfg.capacity_kg_week,
        "kg_h_by_press": cfg.capacity_kg_h,
        "total_kg_week": sum(cfg.capacity_kg_week.values()),
    }

    # --- Backlog (cobertura em semanas) ---
    if overview.get("backlog"):
        bl = overview["backlog"]
        weekly = K.get("production", {}).get("equivalent_weekly_output_kg")
        coverage = round(bl["total_sem_reservas"] / weekly, 1) if (weekly and bl["total_sem_reservas"]) else None
        K["backlog"] = {**bl, "coverage_weeks": coverage}

    # --- Restrições: matrizes bloqueadas ---
    if overview.get("dies_with_problems"):
        dies = overview["dies_with_problems"]
        K["blocked_dies"] = {
            "count": len(dies),
            "blocked_kg": round(sum(d["kg"] for d in dies if d["kg"])),
            "items": dies,
        }

    return result


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    cfg = ExtrusionKPIConfig()
    if len(sys.argv) > 1:
        cfg.data_dir = sys.argv[1]
    print(json.dumps(compute_kpis(cfg), indent=2, ensure_ascii=False, default=str))
