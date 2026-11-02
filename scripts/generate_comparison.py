"""Compara la regresión lineal original con la previsión zero-shot de TimesFM 2.0."""

from __future__ import annotations

import json

from report_common import (
    DATA_DIR,
    FORECAST_YEARS,
    HISTORY_PATH,
    REPORTS_DIR,
    ROOT,
    STYLE,
    format_int,
    format_percent,
    format_signed,
    load_csv,
    svg_chart,
    to_int,
)

BASELINE_PATH = DATA_DIR / "regresion_baseline.csv"
FORECAST_JSON = DATA_DIR / "timesfm_forecast.json"
OUTPUT_HTML = REPORTS_DIR / "comparativa_modelos.html"


def comparison_rows(
    baseline: list[float], timesfm_point: list[float], q10: list[float], q90: list[float]
) -> tuple[str, list[int]]:
    """Las diferencias se calculan sobre los enteros mostrados para que cuadren con la tabla."""
    baseline = [to_int(value) for value in baseline]
    timesfm_point = [to_int(value) for value in timesfm_point]
    gaps = [timesfm_point[index] - baseline[index] for index in range(len(FORECAST_YEARS))]
    rows = []
    for index, year in enumerate(FORECAST_YEARS):
        gap = gaps[index]
        percent = gap / baseline[index] * 100
        inside = q10[index] <= baseline[index] <= q90[index]
        rows.append(
            "<tr>"
            f"<td>{year}</td>"
            f"<td>{format_int(baseline[index])}</td>"
            f"<td>{format_int(timesfm_point[index])}</td>"
            f'<td class="{"up" if gap >= 0 else "down"}">{format_signed(gap)}</td>'
            f'<td class="{"up" if gap >= 0 else "down"}">{format_percent(percent)}</td>'
            f"<td>{'Sí' if inside else 'No'}</td>"
            "</tr>"
        )
    return "".join(rows), gaps


def render_report(
    history: list[dict[str, int]], baseline: list[dict[str, int]], forecast: dict
) -> str:
    years = [row["anio"] for row in history]
    accidents = [row["accidentes_con_baja"] for row in history]
    deaths = [row["mortales"] for row in history]
    accident_reg = [float(row["accidentes_regresion"]) for row in baseline]
    death_reg = [float(row["mortales_regresion"]) for row in baseline]
    accident_fm = forecast["series"]["accidentes_con_baja"]
    death_fm = forecast["series"]["mortales"]

    accident_rows, accident_gaps = comparison_rows(
        accident_reg, accident_fm["point"], accident_fm["q10"], accident_fm["q90"]
    )
    death_rows, death_gaps = comparison_rows(
        death_reg, death_fm["point"], death_fm["q10"], death_fm["q90"]
    )

    accident_chart = svg_chart(
        years,
        accidents,
        [
            {"key": "regresion", "label": "Regresión lineal", "values": accident_reg},
            {"key": "timesfm", "label": "TimesFM 2.0", "values": accident_fm["point"]},
        ],
        "Comparativa de accidentes con baja",
        band=(accident_fm["q10"], accident_fm["q90"]),
    )
    death_chart = svg_chart(
        years,
        deaths,
        [
            {"key": "regresion", "label": "Regresión lineal", "values": death_reg},
            {"key": "timesfm", "label": "TimesFM 2.0", "values": death_fm["point"]},
        ],
        "Comparativa de accidentes mortales",
        band=(death_fm["q10"], death_fm["q90"]),
    )

    accident_reg_change = (accident_reg[-1] / accidents[-1] - 1) * 100
    accident_fm_change = (accident_fm["point"][-1] / accidents[-1] - 1) * 100
    death_reg_change = (death_reg[-1] / deaths[-1] - 1) * 100
    death_fm_change = (death_fm["point"][-1] / deaths[-1] - 1) * 100
    accident_gap_2030 = accident_gaps[-1]
    death_gap_2030 = death_gaps[-1]

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Regresión frente a TimesFM 2.0</title>
<style>{STYLE}</style></head><body><main>
<span class="tag">COMPARATIVA DE MODELOS</span>
<h1>Regresión lineal frente a TimesFM 2.0</h1>
<p class="lead">Las dos previsiones 2026–2030 se calculan sobre el mismo histórico 2008–2025, pero con enfoques distintos: la regresión usa variables económicas rezagadas (afiliación, vivienda iniciada y EIPIC) y TimesFM 2.0 extrapola la serie en modo zero-shot sin ninguna variable externa.</p>
<section class="kpis">
  <div class="card kpi"><span>Accidentes 2030 · diferencia</span><strong>{format_signed(accident_gap_2030)}</strong><span>TimesFM frente a la regresión</span></div>
  <div class="card kpi"><span>Mortales 2030 · diferencia</span><strong>{format_signed(death_gap_2030)}</strong><span>TimesFM frente a la regresión</span></div>
  <div class="card kpi"><span>Base común</span><strong>2008–2025</strong><span>18 observaciones anuales</span></div>
</section>

<section class="card"><h2>Accidentes con baja</h2>{accident_chart}
<p class="note">La banda naranja es el intervalo q10–q90 de TimesFM.</p></section>
<section class="card"><h2>Accidentes con baja · cifras</h2>
<table><thead><tr><th>Año</th><th>Regresión</th><th>TimesFM 2.0</th><th>Diferencia</th><th>Diferencia %</th><th>¿Regresión dentro de q10–q90?</th></tr></thead><tbody>{accident_rows}</tbody></table></section>

<section class="card"><h2>Accidentes mortales</h2>{death_chart}</section>
<section class="card"><h2>Accidentes mortales · cifras</h2>
<table><thead><tr><th>Año</th><th>Regresión</th><th>TimesFM 2.0</th><th>Diferencia</th><th>Diferencia %</th><th>¿Regresión dentro de q10–q90?</th></tr></thead><tbody>{death_rows}</tbody></table></section>

<section class="card"><h2>Qué diferencias aparecen</h2>
<p><strong>Accidentes con baja:</strong> los modelos discrepan en el signo de la tendencia. Partiendo de {format_int(accidents[-1])} accidentes en 2025, la regresión sube hasta {format_int(accident_reg[-1])} en 2030 ({format_percent(accident_reg_change)}) porque la vivienda iniciada prevista crece y arrastra la exposición. TimesFM proyecta {format_int(accident_fm["point"][-1])} ({format_percent(accident_fm_change)}): tras un repunte inicial, prolonga la mejora de los ratios observada en 2024–2025.</p>
<p><strong>Mortales:</strong> aquí coinciden mucho más. Desde {format_int(deaths[-1])} fallecidos en 2025, la regresión llega a {format_int(death_reg[-1])} en 2030 ({format_percent(death_reg_change)}) y TimesFM a {format_int(death_fm["point"][-1])} ({format_percent(death_fm_change)}). La diferencia en ese año es de {format_signed(death_gap_2030)} fallecidos, dentro del intervalo de incertidumbre del modelo fundacional.</p>
<p><strong>Incertidumbre:</strong> TimesFM sí cuantifica su propia incertidumbre y esa es la diferencia metodológica más relevante. La banda q10–q90 de accidentes tiene una amplitud de {format_int(accident_fm["q90"][0] - accident_fm["q10"][0])} accidentes en 2026 y de {format_int(accident_fm["q90"][-1] - accident_fm["q10"][-1])} en 2030, señal de que con 18 datos anuales el horizonte largo es poco informativo. La regresión ofrece un único número sin banda, lo que transmite una falsa precisión.</p>
<p class="note">Ninguna de las dos previsiones es oficial. La regresión es sensible a los supuestos de vivienda iniciada y TimesFM ignora por completo el contexto económico; la lectura útil es la comparación de trayectorias, no la cifra exacta.</p>
</section>
</main></body></html>"""


def main() -> None:
    history = load_csv(HISTORY_PATH)
    baseline = load_csv(BASELINE_PATH)
    forecast = json.loads(FORECAST_JSON.read_text(encoding="utf-8"))
    OUTPUT_HTML.write_text(render_report(history, baseline, forecast), encoding="utf-8")
    print(f"Generado {OUTPUT_HTML.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
