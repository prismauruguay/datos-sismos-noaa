"""Genera data/terremotos.csv con terremotos REALES (1926-2025).

Fuente: NOAA NCEI - Global Significant Earthquake Database
https://www.ngdc.noaa.gov/hazel/view/hazards/earthquake/search

Incluye los terremotos "significativos": con víctimas, daños importantes,
magnitud >= 7.5, intensidad MMI >= X o que generaron tsunami.

Notas sobre las columnas:
- magnitud: magnitud del sismo (campo eqMagnitude de NOAA).
- cantidad_de_victimas: muertes totales (incluye efectos secundarios como tsunamis).
  Vacío = NOAA no reporta el dato.
- hora: UTC. Vacía cuando NOAA no la registra.
- latitud / longitud: epicentro en grados decimales (latitud negativa = sur,
  longitud negativa = oeste).
"""
import json
import urllib.request

import pandas as pd

URL = 'https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes?minYear=1926&maxYear=2025&page={}'
SALIDA = 'data/terremotos.csv'

# Nombre NOAA -> (nombre en español, continente)
PAISES = {
    'AFGHANISTAN': ('Afganistán', 'Asia'),
    'ALBANIA': ('Albania', 'Europa'),
    'ALGERIA': ('Argelia', 'África'),
    'ANTARCTICA': ('Antártida', 'Antártida'),
    'ANTIGUA AND BARBUDA': ('Antigua y Barbuda', 'América del Norte'),
    'ARGENTINA': ('Argentina', 'América del Sur'),
    'ARMENIA': ('Armenia', 'Asia'),
    'ATLANTIC OCEAN': ('Océano Atlántico', 'Océano'),
    'AUSTRALIA': ('Australia', 'Oceanía'),
    'AUSTRIA': ('Austria', 'Europa'),
    'AZERBAIJAN': ('Azerbaiyán', 'Asia'),
    'AZORES (PORTUGAL)': ('Azores (Portugal)', 'Europa'),
    'BANGLADESH': ('Bangladés', 'Asia'),
    'BELGIUM': ('Bélgica', 'Europa'),
    'BERING SEA': ('Mar de Bering', 'Océano'),
    'BHUTAN': ('Bután', 'Asia'),
    'BOLIVIA': ('Bolivia', 'América del Sur'),
    'BOSNIA-HERZEGOVINA': ('Bosnia y Herzegovina', 'Europa'),
    'BRAZIL': ('Brasil', 'América del Sur'),
    'BULGARIA': ('Bulgaria', 'Europa'),
    'BURUNDI': ('Burundi', 'África'),
    'CAMEROON': ('Camerún', 'África'),
    'CANADA': ('Canadá', 'América del Norte'),
    'CHILE': ('Chile', 'América del Sur'),
    'CHINA': ('China', 'Asia'),
    'COLOMBIA': ('Colombia', 'América del Sur'),
    'COMOROS': ('Comoras', 'África'),
    'CONGO': ('Congo', 'África'),
    'COSTA RICA': ('Costa Rica', 'América del Norte'),
    'CROATIA': ('Croacia', 'Europa'),
    'CUBA': ('Cuba', 'América del Norte'),
    'CYPRUS': ('Chipre', 'Asia'),
    'CZECH REPUBLIC': ('República Checa', 'Europa'),
    'DJIBOUTI': ('Yibuti', 'África'),
    'DOMINICAN REPUBLIC': ('República Dominicana', 'América del Norte'),
    'ECUADOR': ('Ecuador', 'América del Sur'),
    'EGYPT': ('Egipto', 'África'),
    'EL SALVADOR': ('El Salvador', 'América del Norte'),
    'ETHIOPIA': ('Etiopía', 'África'),
    'FIJI': ('Fiyi', 'Oceanía'),
    'FRANCE': ('Francia', 'Europa'),
    'GABON': ('Gabón', 'África'),
    'GEORGIA': ('Georgia', 'Asia'),
    'GERMANY': ('Alemania', 'Europa'),
    'GHANA': ('Ghana', 'África'),
    'GREECE': ('Grecia', 'Europa'),
    'GREENLAND': ('Groenlandia', 'América del Norte'),
    'GUADELOUPE': ('Guadalupe', 'América del Norte'),
    'GUATEMALA': ('Guatemala', 'América del Norte'),
    'GUINEA': ('Guinea', 'África'),
    'HAITI': ('Haití', 'América del Norte'),
    'HONDURAS': ('Honduras', 'América del Norte'),
    'HUNGARY': ('Hungría', 'Europa'),
    'ICELAND': ('Islandia', 'Europa'),
    'INDIA': ('India', 'Asia'),
    'INDIAN OCEAN': ('Océano Índico', 'Océano'),
    'INDONESIA': ('Indonesia', 'Asia'),
    'IRAN': ('Irán', 'Asia'),
    'IRAQ': ('Irak', 'Asia'),
    'ISRAEL': ('Israel', 'Asia'),
    'ITALY': ('Italia', 'Europa'),
    'JAMAICA': ('Jamaica', 'América del Norte'),
    'JAPAN': ('Japón', 'Asia'),
    'JORDAN': ('Jordania', 'Asia'),
    'KAZAKHSTAN': ('Kazajistán', 'Asia'),
    'KENYA': ('Kenia', 'África'),
    'KERMADEC ISLANDS (NEW ZEALAND)': ('Islas Kermadec (Nueva Zelanda)', 'Oceanía'),
    'KYRGYZSTAN': ('Kirguistán', 'Asia'),
    'LAOS': ('Laos', 'Asia'),
    'LEBANON': ('Líbano', 'Asia'),
    'LIBYA': ('Libia', 'África'),
    'MADAGASCAR': ('Madagascar', 'África'),
    'MALAWI': ('Malaui', 'África'),
    'MALAYSIA': ('Malasia', 'Asia'),
    'MARTINIQUE': ('Martinica', 'América del Norte'),
    'MEXICO': ('México', 'América del Norte'),
    'MICRONESIA, FED. STATES OF': ('Micronesia', 'Oceanía'),
    'MONGOLIA': ('Mongolia', 'Asia'),
    'MONTENEGRO': ('Montenegro', 'Europa'),
    'MOROCCO': ('Marruecos', 'África'),
    'MOZAMBIQUE': ('Mozambique', 'África'),
    'MYANMAR (BURMA)': ('Myanmar', 'Asia'),
    'NEPAL': ('Nepal', 'Asia'),
    'NETHERLANDS': ('Países Bajos', 'Europa'),
    'NEW CALEDONIA': ('Nueva Caledonia', 'Oceanía'),
    'NEW ZEALAND': ('Nueva Zelanda', 'Oceanía'),
    'NICARAGUA': ('Nicaragua', 'América del Norte'),
    'NORTH MACEDONIA': ('Macedonia del Norte', 'Europa'),
    'NORWAY': ('Noruega', 'Europa'),
    'PACIFIC OCEAN': ('Océano Pacífico', 'Océano'),
    'PAKISTAN': ('Pakistán', 'Asia'),
    'PANAMA': ('Panamá', 'América del Norte'),
    'PAPUA NEW GUINEA': ('Papúa Nueva Guinea', 'Oceanía'),
    'PERU': ('Perú', 'América del Sur'),
    'PHILIPPINES': ('Filipinas', 'Asia'),
    'POLAND': ('Polonia', 'Europa'),
    'PORTUGAL': ('Portugal', 'Europa'),
    'ROMANIA': ('Rumania', 'Europa'),
    'RUSSIA': ('Rusia', None),  # se decide por longitud (Europa / Asia)
    'RWANDA': ('Ruanda', 'África'),
    'SAMOA': ('Samoa', 'Oceanía'),
    'SAUDI ARABIA': ('Arabia Saudita', 'Asia'),
    'SERBIA': ('Serbia', 'Europa'),
    'SLOVAKIA': ('Eslovaquia', 'Europa'),
    'SLOVENIA': ('Eslovenia', 'Europa'),
    'SOLOMON ISLANDS': ('Islas Salomón', 'Oceanía'),
    'SOLOMON SEA': ('Mar de Salomón', 'Océano'),
    'SOUTH AFRICA': ('Sudáfrica', 'África'),
    'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS': ('Georgias del Sur y Sandwich del Sur', 'Antártida'),
    'SOUTH KOREA': ('Corea del Sur', 'Asia'),
    'SOUTH SUDAN': ('Sudán del Sur', 'África'),
    'SPAIN': ('España', 'Europa'),
    'SUDAN': ('Sudán', 'África'),
    'SWITZERLAND': ('Suiza', 'Europa'),
    'SYRIA': ('Siria', 'Asia'),
    'TAIWAN': ('Taiwán', 'Asia'),
    'TAJIKISTAN': ('Tayikistán', 'Asia'),
    'TANZANIA': ('Tanzania', 'África'),
    'THAILAND': ('Tailandia', 'Asia'),
    'TOGO': ('Togo', 'África'),
    'TONGA': ('Tonga', 'Oceanía'),
    'TRINIDAD AND TOBAGO': ('Trinidad y Tobago', 'América del Norte'),
    'TUNISIA': ('Túnez', 'África'),
    'TURKEY': ('Turquía', 'Asia'),
    'TURKMENISTAN': ('Turkmenistán', 'Asia'),
    'UGANDA': ('Uganda', 'África'),
    'UK': ('Reino Unido', 'Europa'),
    'UK TERRITORY': ('Territorio del Reino Unido', 'Océano'),
    'UKRAINE': ('Ucrania', 'Europa'),
    'USA': ('Estados Unidos', 'América del Norte'),
    'USA TERRITORY': ('Territorio de EE.UU.', 'Oceanía'),
    'UZBEKISTAN': ('Uzbekistán', 'Asia'),
    'VANUATU': ('Vanuatu', 'Oceanía'),
    'VENEZUELA': ('Venezuela', 'América del Sur'),
    'VIETNAM': ('Vietnam', 'Asia'),
    'WALLIS AND FUTUNA (FRENCH TERRITORY)': ('Wallis y Futuna (Francia)', 'Oceanía'),
    'YEMEN': ('Yemen', 'Asia'),
    'ZAMBIA': ('Zambia', 'África'),
}


# NOAA usa puntos cardinales para indicar la zona del país ("ITALY: S" = sur de Italia)
DIRECCIONES = {
    'N': 'Norte', 'S': 'Sur', 'E': 'Este', 'W': 'Oeste',
    'Ne': 'Noreste', 'Nw': 'Noroeste', 'Se': 'Sureste', 'Sw': 'Suroeste',
    'Central': 'Centro',
}


def separar_ubicacion(location_name):
    """locationName viene como "PAIS:  REGION:  LUGAR", con cantidad de partes variable.

    - 2 partes ("JAPAN: KUMAMOTO"): es una zona, va a region y lugar queda vacío.
    - 3 o más ("ITALY: CATANIA: RAGALNA"): region = 2da parte, lugar = última.
    - Un punto cardinal se traduce en region y se descarta en lugar.
    """
    partes = [p.strip().title() for p in location_name.split(':') if p.strip()]
    region = partes[1] if len(partes) > 1 else ''
    lugar = partes[-1] if len(partes) > 2 else ''
    region = DIRECCIONES.get(region, region)
    if lugar in DIRECCIONES:
        lugar = ''
    return region, lugar


def descargar():
    items, pagina, total = [], 1, 1
    while pagina <= total:
        with urllib.request.urlopen(URL.format(pagina), timeout=120) as r:
            datos = json.load(r)
        items += datos['items']
        total = datos['totalPages']
        pagina += 1
    return items


def a_fila(ev):
    pais, continente = PAISES.get(ev['country'], (ev['country'].title(), None))
    if ev['country'] == 'RUSSIA':
        continente = 'Europa' if ev.get('longitude', 100) < 60 else 'Asia'

    region, lugar = separar_ubicacion(ev['locationName'])

    hora = ''
    if 'hour' in ev:
        hora = f"{ev['hour']:02d}:{ev.get('minute', 0):02d}:{int(ev.get('second', 0)):02d}"

    return {
        'fecha': f"{ev['year']:04d}-{ev['month']:02d}-{ev['day']:02d}",
        'hora': hora,
        'continente': continente,
        'pais': pais,
        'lugar': lugar,
        'region': region,
        'magnitud': ev.get('eqMagnitude'),
        'cantidad_de_victimas': ev.get('deathsTotal', ev.get('deaths')),
        'latitud': ev.get('latitude'),
        'longitud': ev.get('longitude'),
    }


if __name__ == '__main__':
    eventos = descargar()
    # se descartan los pocos eventos sin mes o día conocido
    completos = [ev for ev in eventos if 'month' in ev and 'day' in ev]
    df = pd.DataFrame([a_fila(ev) for ev in completos])
    df['cantidad_de_victimas'] = df['cantidad_de_victimas'].astype('Int64')
    df = df.sort_values(['fecha', 'hora'], ascending=False)
    df.to_csv(SALIDA, index=False)
    print(f'{len(df)} terremotos guardados en {SALIDA} ({len(eventos) - len(completos)} descartados sin fecha completa)')
