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
6. **Simulacion 2026-2030** - Proyeccion por regresion y ratios normalizados.
7. **Modelo predictivo** - Primer modelo exploratorio con predicciones y errores por ano.

## Hallazgos destacados

- Cobertura temporal consolidada: **2008-2025**.
- Reduccion del indice de incidencia en el periodo: **-47,5%**.
- Reduccion de accidentes por 1.000 afiliados: **-33,6%**.
- Proyeccion central de accidentes en 2030: **104.498**.
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

## Estructura

```
index.html         Aplicacion (hero, barra lateral, visor iframe, modo claro/oscuro)
assets/
  styles.css       Sistema de diseno (responsive, tema claro/oscuro)
  app.js           Navegacion, routing por hash y carga de informes
reports/           Los siete informes HTML autocontenidos
```
