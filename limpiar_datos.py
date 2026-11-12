"""Genera data/terremotos_limpio.csv a partir de data/terremotos.csv.

Decisiones de limpieza (justificadas en el manual):
- Víctimas vacías -> 0: NOAA solo registra el campo cuando hubo muertes.
  La columna victimas_informadas conserva qué registros venían sin dato.
- Se excluyen los sismos sin magnitud informada y los de magnitud menor a 4.
- Se excluyen 4 eventos cuyas víctimas se atribuyen a erupciones volcánicas
  (Nyiragongo 2002 y 2021, Pinatubo 1991 y St. Helens 1980).
- Se elimina la columna lugar (vacía en la mayoría de los registros) y se agregan anio y mes.
"""
import pandas as pd

df = pd.read_csv('data/terremotos.csv', parse_dates=['fecha'])

df['victimas_informadas'] = df['cantidad_de_victimas'].notna()
df['cantidad_de_victimas'] = df['cantidad_de_victimas'].fillna(0).astype(int)

df = df[df['magnitud'].notna() & (df['magnitud'] >= 4)]

erupciones = [('2021-05-25', 'Ruanda'), ('2002-01-17', 'Ruanda'),
              ('1991-06-15', 'Filipinas'), ('1980-05-18', 'Estados Unidos')]
for fecha, pais in erupciones:
    df = df[~((df['fecha'] == fecha) & (df['pais'] == pais))]

df = df.drop(columns=['lugar'])
df['anio'] = df['fecha'].dt.year
df['mes'] = df['fecha'].dt.month

df.to_csv('data/terremotos_limpio.csv', index=False)
print(f'{len(df)} sismos guardados en data/terremotos_limpio.csv')
