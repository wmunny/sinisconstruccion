# Siniestralidad Laboral en el Sector Construccion en Espana (2008-2025)

Dashboard visual e interactivo que recopila el analisis de la evolucion de la
siniestralidad laboral en el sector de la construccion en Espana y su relacion
con la actividad economica, la vivienda y la exposicion laboral.

## Contenido

El sitio es una aplicacion tipo panel (barra lateral + visor) que reune siete
informes, pensados para leerse en la siguiente ruta recomendada:

1. **Informe final** - Lectura ejecutiva: metodologia, hallazgos, focos de riesgo y limites.
2. **Historico 2008-2025** - Graficas de evolucion: incidencia, accidentes, mortalidad, afiliacion, vivienda, Euribor y EIPIC.
3. **Evolucion normalizada** - Accidentes y mortales normalizados por viviendas iniciadas.
4. **Formas mortales** - Tipos de accidente mortal por forma y estrategias preventivas.
5. **Calor y PNT** - Analisis mensual de patologias no traumaticas y meses calidos.
6. **Prediccion 2026-2030** - Prevision zero-shot con TimesFM 2.0 e intervalos cuantiles.
7. **Regresion vs TimesFM** - Comparativa entre la proyeccion por regresion y la prevision zero-shot.

## Hallazgos destacados

- Cobertura temporal consolidada: **2008-2025**.
- Reduccion del indice de incidencia en el periodo: **-47,5%**.
- Reduccion de accidentes por 1.000 afiliados: **-33,6%**.
- La prediccion 2026-2030 se genera con el checkpoint abierto
  `google/timesfm-2.0-500m-pytorch`.
- La afiliacion y las viviendas iniciadas son los factores mas correlacionados con
  los accidentes con baja (r > 0,95), mientras que la mortalidad depende ademas de
  la composicion y peligrosidad de las tareas.

## Fuentes

Datos oficiales y trazables: MITES (Estadistica de Accidentes de Trabajo), INSST,
Seguridad Social / Observatorio Industrial de la Construccion, ISTAC (vivienda),
EIPIC (Ministerio de Transportes) y BCE (Euribor).

## Uso local

Al usar rutas relativas y contenido autocontenido, basta con servir la carpeta:

```bash
python -m http.server 8000
```

Y abrir `http://localhost:8000`.

## Regenerar la prediccion TimesFM

TimesFM 2.0 requiere Python 3.10 o 3.11. La primera ejecucion descarga el
checkpoint de Hugging Face (aproximadamente 2 GB):

```bash
py -3.11 -m venv .venv
.venv\Scripts\pip install -r requirements-timesfm.txt
.venv\Scripts\python scripts\generate_timesfm_forecast.py
```

En Linux/macOS, crear el entorno con `python3.11 -m venv .venv` y sustituir
`.venv\Scripts\` por `.venv/bin/`. El script lee
`data/siniestralidad_anual.csv` y vuelve a generar:

- `data/timesfm_forecast.json`, resultado estructurado.
- `reports/simulacion_5_anios.html`, informe visible en el dashboard.

La comparativa con la regresion original se genera aparte y no necesita el
modelo, porque reutiliza el JSON anterior y `data/regresion_baseline.csv`:

```bash
.venv\Scripts\python scripts\generate_comparison.py
```

Se utiliza frecuencia anual, dos series univariantes independientes (accidentes
con baja y mortales), contexto 2008-2025 y horizonte 2026-2030. Es una
estimacion exploratoria: 18 observaciones son una muestra corta y el modelo no
incorpora variables externas ni demuestra causalidad.

## Estructura

```
index.html         Aplicacion (hero, barra lateral, visor iframe, modo claro/oscuro)
assets/
  styles.css       Sistema de diseno (responsive, tema claro/oscuro)
  app.js           Navegacion, routing por hash y carga de informes
reports/           Los siete informes HTML autocontenidos
data/              Series de entrada, baseline de regresion y prediccion generada
scripts/           Generadores reproducibles (TimesFM 2.0 y comparativa)
```
