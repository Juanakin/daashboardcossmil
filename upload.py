import pandas as pd
from postgress import neon_connection  # Importamos la conexión configurada
# Cargar hoja específica, saltando las filas de subtítulos y poniendo encabezados en la fila correcta
# Según tu imagen, los encabezados están en la fila 2 (índice 2 en 0-based)
df = pd.read_excel("cossmil.xlsx", sheet_name="PRODUCCION", header=2)

# Eliminar filas completamente vacías
df = df.dropna(how='all')

# Eliminar filas donde la columna 'DIA' contenga nombres de meses o sea nula
meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio","julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre","dia"]

df = df[df['DIA'].astype(str).str.lower().apply(lambda x: x not in meses)]

# También eliminar filas donde 'DIA' contenga subtítulos, por ejemplo 'ABRIL 2023'
df = df[~df['DIA'].astype(str).str.contains(r"\d{4}", na=False)]  # elimina filas con años

# También eliminar filas donde 'DIA' contenga subtítulos, por ejemplo 'ABRIL 2023'
df = df[~df['FECHA'].astype(str).str.contains(r"TOTAL", na=False)]  # elimina filas con años

# Opcional: Resetear índice después de la limpieza
df = df.reset_index(drop=True)

# Guardar limpio si quieres
df.to_csv("limpio.csv", index=False)

try:
    engine = neon_connection.connect()

    # 3. Cargar a PostgreSQL en Neon
    df.to_sql(
        name='produccion',            # Nombre de la tabla en PostgreSQL
        con=engine,
        if_exists='replace',       # Opciones: 'fail', 'replace', 'append'
        index=False,
        chunksize=500,            # Ideal para Neon serverless
        method='multi'            # Inserciones más eficientes
    )
    print("\n✅ Datos cargados exitosamente a la tabla 'produccion' en Neon")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    raise