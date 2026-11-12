# Sismos significativos del mundo, 1926–2025 (NOAA)

Datos reales de los terremotos significativos registrados entre 1926 y 2025, preparados para el
estudio de Ciencia de Datos con Python y pandas.

## Fuente

Los datos provienen de la base de datos de terremotos significativos de NOAA:

> National Geophysical Data Center / World Data Service (NGDC/WDS): NCEI/WDS Global Significant
> Earthquake Database. NOAA National Centers for Environmental Information. doi:10.7289/V5TD9V7K.
> Consultado el 12 de noviembre de 2026.

- Buscador web: https://www.ngdc.noaa.gov/hazel/view/hazards/earthquake/search
- API utilizada: https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes

Los datos de NOAA son de dominio público. Si los usás, citá la fuente original como se indica arriba.

**¿Qué es un sismo "significativo"?** NOAA incluye un evento si cumple al menos una condición:
causó víctimas o daños importantes (aproximadamente un millón de dólares o más), tuvo magnitud 7.5 o
mayor, alcanzó intensidad X o mayor en la escala de Mercalli modificada, o generó un tsunami.
Por eso **no es un catálogo de todos los sismos**: los sismos chicos aparecen solo si causaron daño.

## Archivos

| Archivo | Contenido |
|---|---|
| `data/terremotos.csv` | Datos crudos: 3493 sismos tal como los informa NOAA (con valores faltantes). |
| `data/terremotos_limpio.csv` | Datos limpios: 3280 sismos, resultado de `limpiar_datos.py`. |
| `descargar_datos_noaa.py` | Descarga los datos desde la API de NOAA y genera `terremotos.csv`. |
| `limpiar_datos.py` | Aplica las decisiones de limpieza y genera `terremotos_limpio.csv`. |

## Cómo cargar los datos

No hace falta descargar nada: pandas puede leer el CSV directamente desde GitHub.

```python
import pandas as pd

url = "https://raw.githubusercontent.com/USUARIO/REPOSITORIO/main/data/terremotos.csv"
df_sismos = pd.read_csv(url, parse_dates=["fecha"])
print(df_sismos.head())
```

## Columnas de `terremotos.csv`

| Columna | Descripción |
|---|---|
| `fecha` | Fecha del sismo (AAAA-MM-DD). |
| `hora` | Hora UTC (vacía si NOAA no la registra). |
| `continente` | Continente. "América del Norte" incluye América Central y el Caribe; "Océano" agrupa los sismos que NOAA ubica en el mar. |
| `pais` | País, en español. |
| `lugar` | Localidad, cuando NOAA la informa (vacía en la mayoría de los registros). |
| `region` | Región o zona dentro del país. |
| `magnitud` | Magnitud del sismo (campo `eqMagnitude` de NOAA). Es la energía liberada, no la intensidad percibida. |
| `cantidad_de_victimas` | Muertes totales, incluidos efectos secundarios como tsunamis. Vacío = NOAA no informa el dato. |
| `latitud`, `longitud` | Epicentro en grados decimales (negativo = sur / oeste). |

`terremotos_limpio.csv` no incluye `lugar` y agrega `victimas_informadas` (indica si NOAA informaba
el dato de víctimas), `anio` y `mes`.

## Decisiones de limpieza

1. Las víctimas vacías se completan con 0, porque NOAA solo registra el campo cuando hubo muertes.
   La columna `victimas_informadas` conserva qué registros venían sin dato.
2. Se excluyen 176 sismos sin magnitud informada y 33 de magnitud menor a 4.
3. Se excluyen 4 eventos cuyas víctimas se atribuyen a erupciones volcánicas: Nyiragongo (2002 y
   2021), Pinatubo (1991) y St. Helens (1980).

## Limitaciones

- El registro no es homogéneo en el tiempo: en las primeras décadas se detectaban y registraban
  menos sismos que en la actualidad.
- En sismos antiguos, un dato de víctimas vacío podría ser un dato perdido y no un 0 real.
- Los totales de víctimas no tienen en cuenta la población de cada país o continente, por lo que no
  miden el riesgo por persona.
- NOAA puede actualizar o corregir registros. Estos archivos son una copia fija descargada en
  noviembre de 2026; si volvés a ejecutar `descargar_datos_noaa.py`, los resultados pueden variar
  levemente.

## Regenerar los datos

```bash
pip install pandas
python descargar_datos_noaa.py
python limpiar_datos.py
```
