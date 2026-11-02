"""Utilidades compartidas por los generadores de informes del dashboard."""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
HISTORY_PATH = DATA_DIR / "siniestralidad_anual.csv"
FORECAST_YEARS = list(range(2026, 2031))

STYLE = """
:root{--ink:#172033;--muted:#667085;--card:#fff;--line:#d9e0ea;--brand:#ef6c35;--blue:#2878bd;--green:#128c6a}
*{box-sizing:border-box} body{margin:0;background:#f4f6f9;color:var(--ink);font:15px/1.55 system-ui,sans-serif}
main{max-width:1160px;margin:auto;padding:32px 22px 64px} h1{font-size:clamp(28px,4vw,45px);margin:0 0 8px}
h2{margin:0 0 14px} .lead{font-size:18px;color:var(--muted);max-width:900px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:25px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px;margin:16px 0;box-shadow:0 6px 20px #1b263b0b}
.kpi strong{display:block;font-size:30px} .kpi span,.note{color:var(--muted)} .tag{color:var(--brand);font-weight:750}
.chart{display:block;width:100%;min-height:260px} .grid line{stroke:#e5eaf1} .grid text,.axis text{fill:#667085;font-size:12px}
.actual,.serie{fill:none;stroke-width:3} .actual{stroke:var(--blue)}
.serie-timesfm{stroke:var(--brand);stroke-dasharray:8 5} .serie-regresion{stroke:var(--green);stroke-dasharray:2 6}
.band{fill:#ef6c3525} .divider{stroke:#98a2b3;stroke-dasharray:3 5}
.legend text{font-size:13px;font-weight:700} .legend .l-actual{fill:var(--blue)} .legend .l-timesfm{fill:var(--brand)} .legend .l-regresion{fill:var(--green)}
table{width:100%;border-collapse:collapse} th,td{padding:11px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left} .up{color:#b42318;font-weight:650} .down{color:#128c6a;font-weight:650}
code{background:#eef2f6;padding:2px 5px;border-radius:4px} @media(max-width:700px){.kpis{grid-template-columns:1fr}.card{overflow:auto}}
"""


def load_csv(path: Path) -> list[dict[str, int]]:
    with path.open(encoding="utf-8", newline="") as source:
        return [{key: int(value) for key, value in row.items()} for row in csv.DictReader(source)]


def to_int(value: float) -> int:
    return math.floor(value + 0.5)


def format_int(value: float) -> str:
    return f"{to_int(value):,}".replace(",", ".")


def format_signed(value: float) -> str:
    return ("+" if value >= 0 else "−") + format_int(abs(value))


def format_percent(value: float) -> str:
    return f"{'+' if value >= 0 else '−'}{abs(value):.1f} %".replace(".", ",")


def svg_chart(
    years: list[int],
    actual: list[int],
    series: list[dict],
    label: str,
    band: tuple[list[float], list[float]] | None = None,
) -> str:
    """Dibuja el histórico y una o varias trayectorias previstas para 2026-2030."""
    width, height = 960, 360
    left, right, top, bottom = 72, 24, 40, 48
    all_years = years + FORECAST_YEARS
    ceiling = actual + [value for item in series for value in item["values"]]
    if band:
        ceiling = ceiling + band[1]
    high = max(ceiling) * 1.12

    def x(year: float) -> float:
        return left + (year - all_years[0]) * (width - left - right) / (all_years[-1] - all_years[0])

    def y(value: float) -> float:
        return top + (high - value) * (height - top - bottom) / high

    def path(points_years: list[int], values: list[float]) -> str:
        return " ".join(f"{x(year):.1f},{y(value):.1f}" for year, value in zip(points_years, values))

    grid = "".join(
        f'<line x1="{left}" y1="{y(high * step / 4):.1f}" x2="{width-right}" y2="{y(high * step / 4):.1f}"/>'
        f'<text x="{left-10}" y="{y(high * step / 4)+4:.1f}" text-anchor="end">{format_int(high * step / 4)}</text>'
        for step in range(5)
    )
    ticks = "".join(
        f'<text x="{x(year):.1f}" y="{height-17}" text-anchor="middle">{year}</text>'
        for year in all_years
        if year % 2 == 0 or year == all_years[-1]
    )
    band_svg = ""
    if band:
        lower, upper = band
        points = path(FORECAST_YEARS, upper) + " " + path(FORECAST_YEARS[::-1], lower[::-1])
        band_svg = f'<polygon class="band" points="{points}"/>'

    lines = "".join(
        f'<polyline class="serie serie-{item["key"]}" points="{path([years[-1]] + FORECAST_YEARS, [actual[-1]] + item["values"])}"/>'
        for item in series
    )
    legend_items = [("actual", "Histórico 2008–2025")] + [(item["key"], item["label"]) for item in series]
    legend = "".join(
        f'<text class="l-{key}" x="{left + index * 240}" y="{top-16}">■ {html.escape(name)}</text>'
        for index, (key, name) in enumerate(legend_items)
    )
    return f"""
    <svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(label)}">
      <g class="grid">{grid}</g>
      <line class="divider" x1="{x(2025.5):.1f}" y1="{top}" x2="{x(2025.5):.1f}" y2="{height-bottom}"/>
      {band_svg}
      <polyline class="actual" points="{path(years, actual)}"/>
      {lines}
      <g class="axis">{ticks}</g>
      <g class="legend">{legend}</g>
    </svg>"""
