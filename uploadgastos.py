import pandas as pd
from postgress import neon_connection  # Importamos la conexión configurada

# Cargar el archivo Excel
df = pd.read_excel("cossmil.xlsx", sheet_name="EGRESOS", header=3)

# Mostrar las primeras filas para diagnóstico
print("Datos originales:")
print(df.head())
print("\nColumnas disponibles:", df.columns.tolist())

# Limpieza de datos
# 1. Eliminar filas completamente vacías
df = df.dropna(how='all')

# 2. Filtrar filas válidas (donde FECHA tiene formato de fecha)
# Primero intentamos convertir FECHA a datetime
df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

# Mantener solo filas donde FECHA es válida (no NaT)
df = df[df['FECHA'].notna()]

# 3. Limpiar la columna MONTO (eliminar comas y convertir a numérico)
df['MONTO'] = df['MONTO'].astype(str).str.replace(',', '').astype(float)

# Verificar resultados
print("\nDatos después de limpieza:")
print(df.head())

# Guardar en CSV
df.to_csv("egresos_limpio.csv", index=False)
print("\nDatos guardados en 'egresos_limpio.csv'")

# 2. Conectar a Neon
try:
    engine = neon_connection.connect()

    # 3. Cargar a PostgreSQL en Neon
    df.to_sql(
        name='egresos',            # Nombre de la tabla en PostgreSQL
        con=engine,
        if_exists='replace',       # Opciones: 'fail', 'replace', 'append'
        index=False,
        chunksize=500,            # Ideal para Neon serverless
        method='multi'            # Inserciones más eficientes
    )
    print("\n✅ Datos cargados exitosamente a la tabla 'egresos' en Neon")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    raise