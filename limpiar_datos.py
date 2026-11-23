"""Genera data/terremotos_limpio.csv a partir de data/terremotos.csv.

Decisiones de limpieza (justificadas en el manual):
- Víctimas vacías -> 0, y la columna victimas_informadas conserva qué registros
  venían sin dato. Un vacío no es un cero (puede ser una cifra desconocida):
  para analizar muertes, usar solo victimas_informadas == True.
- Se excluyen los sismos sin magnitud informada y los de magnitud menor a 4.
- Se elimina la columna lugar (vacía en la mayoría de los registros) y se agregan anio y mes.
"""
import pandas as pd

df = pd.read_csv('data/terremotos.csv', parse_dates=['fecha'])

df['victimas_informadas'] = df['cantidad_de_victimas'].notna()
df['cantidad_de_victimas'] = df['cantidad_de_victimas'].fillna(0).astype(int)

df = df[df['magnitud'].notna() & (df['magnitud'] >= 4)]

df = df.drop(columns=['lugar'])
df['anio'] = df['fecha'].dt.year
df['mes'] = df['fecha'].dt.month

df.to_csv('data/terremotos_limpio.csv', index=False)
print(f'{len(df)} sismos guardados en data/terremotos_limpio.csv')
