"""Genera la previsión 2026-2030 con TimesFM 2.0 y el informe del dashboard."""

from __future__ import annotations

import json

import numpy as np
import timesfm

from report_common import (
    DATA_DIR,
    FORECAST_YEARS,
    HISTORY_PATH,
    REPORTS_DIR,
    ROOT,
    STYLE,
    format_int,
    load_csv,
    svg_chart,
)

OUTPUT_JSON = DATA_DIR / "timesfm_forecast.json"
OUTPUT_HTML = REPORTS_DIR / "simulacion_5_anios.html"
MODEL_DIR = ROOT / ".model-cache" / "timesfm-2.0-500m-pytorch"
CHECKPOINT = "google/timesfm-2.0-500m-pytorch"


def forecast(series: list[int], model: timesfm.TimesFm) -> dict[str, list[float]]:
    point, full = model.forecast([np.asarray(series, dtype=np.float32)], freq=[2])
    quantiles = list(model.quantiles)

    def quantile_values(value: float) -> np.ndarray:
        index = min(range(len(quantiles)), key=lambda i: abs(quantiles[i] - value))
        return full[0, : len(FORECAST_YEARS), index + 1]

    def rounded(values: np.ndarray) -> list[float]:
        return [round(float(value), 1) for value in np.maximum(values, 0)]

    return {
        "point": rounded(point[0, : len(FORECAST_YEARS)]),
        "q10": rounded(quantile_values(0.1)),
        "q90": rounded(quantile_values(0.9)),
    }


def render_report(data: list[dict[str, int]], forecasts: dict[str, dict[str, list[float]]]) -> str:
    years = [row["anio"] for row in data]
    accidents = [row["accidentes_con_baja"] for row in data]
    deaths = [row["mortales"] for row in data]
    accident_fc = forecasts["accidentes_con_baja"]
    death_fc = forecasts["mortales"]

    rows = "".join(
        "<tr>"
        f"<td>{year}</td>"
        f"<td>{format_int(accident_fc['point'][index])}</td>"
        f"<td>{format_int(accident_fc['q10'][index])}–{format_int(accident_fc['q90'][index])}</td>"
        f"<td>{format_int(death_fc['point'][index])}</td>"
        f"<td>{format_int(death_fc['q10'][index])}–{format_int(death_fc['q90'][index])}</td>"
        "</tr>"
        for index, year in enumerate(FORECAST_YEARS)
    )
    accident_chart = svg_chart(
        years,
        accidents,
        [{"key": "timesfm", "label": "TimesFM 2.0", "values": accident_fc["point"]}],
        "Accidentes con baja",
        band=(accident_fc["q10"], accident_fc["q90"]),
    )
    death_chart = svg_chart(
        years,
        deaths,
        [{"key": "timesfm", "label": "TimesFM 2.0", "values": death_fc["point"]}],
        "Accidentes mortales",
        band=(death_fc["q10"], death_fc["q90"]),
    )
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Previsión TimesFM 2026-2030</title>
<style>{STYLE}</style></head><body><main>
<span class="tag">MODELO FUNDACIONAL · ZERO-SHOT</span>
<h1>Previsión de siniestralidad 2026–2030</h1>
<p class="lead">La regresión anterior se ha sustituido por TimesFM 2.0 (500M). El modelo recibe únicamente cada serie anual de 2008–2025 y genera cinco años de previsión sin entrenamiento específico.</p>
<section class="kpis">
  <div class="card kpi"><span>Accidentes en 2030</span><strong>{format_int(accident_fc["point"][-1])}</strong><span>Estimación central TimesFM</span></div>
  <div class="card kpi"><span>Mortales en 2030</span><strong>{format_int(death_fc["point"][-1])}</strong><span>Estimación central TimesFM</span></div>
  <div class="card kpi"><span>Contexto disponible</span><strong>18 años</strong><span>2008–2025 · frecuencia anual</span></div>
</section>
<section class="card"><h2>Accidentes con baja</h2>{accident_chart}</section>
<section class="card"><h2>Accidentes mortales</h2>{death_chart}</section>
<section class="card"><h2>Resultados</h2><table><thead><tr><th>Año</th><th>Accidentes</th><th>Intervalo q10–q90</th><th>Mortales</th><th>Intervalo q10–q90</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="card"><h2>Cómo se ha calculado</h2>
<p>Checkpoint <code>{CHECKPOINT}</code>, backend PyTorch, frecuencia categórica <code>2</code> (anual), inferencia univariante y horizonte de cinco pasos. Las bandas muestran los cuantiles 10 % y 90 % producidos por el modelo.</p>
<p class="note"><strong>Limitación:</strong> 18 observaciones son pocas para evaluar una previsión a cinco años y la serie de mortalidad es especialmente volátil. El resultado es exploratorio, no una previsión oficial ni causal. TimesFM 2.0 no incorpora aquí afiliación, vivienda u otras variables externas.</p>
</section>
</main></body></html>"""


def main() -> None:
    data = load_csv(HISTORY_PATH)
    model = timesfm.TimesFm(
        hparams=timesfm.TimesFmHparams(
            backend="cpu",
            per_core_batch_size=1,
            horizon_len=len(FORECAST_YEARS),
            num_layers=50,
            context_len=32,
            use_positional_embedding=False,
        ),
        checkpoint=timesfm.TimesFmCheckpoint(
            huggingface_repo_id=CHECKPOINT,
            local_dir=str(MODEL_DIR),
        ),
    )
    forecasts = {
        "accidentes_con_baja": forecast([row["accidentes_con_baja"] for row in data], model),
        "mortales": forecast([row["mortales"] for row in data], model),
    }
    payload = {
        "model": CHECKPOINT,
        "frequency": "anual",
        "history": [data[0]["anio"], data[-1]["anio"]],
        "forecast_years": FORECAST_YEARS,
        "series": forecasts,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_HTML.write_text(render_report(data, forecasts), encoding="utf-8")
    print(f"Generados {OUTPUT_JSON.relative_to(ROOT)} y {OUTPUT_HTML.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
