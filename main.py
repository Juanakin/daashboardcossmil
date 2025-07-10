import streamlit as st
import pandas as pd
import plotly.express as px
from postgress import neon_connection  # Importamos la conexión configurada


traduccion_columnas = {
    'SEMANA': 'Detalle Semanal',
    'PRODUCCION': 'Producción Kg.',
    'KGCOMERCIALIZACION': 'Comercialización Kg.',
    'BSCOMERCIALIZACION': 'Comercialización Bs.',
    'SALDOALMACENES': 'Saldo en Almacenes',
    'INGRESOS': 'Ingresos por Ventas Bs.',
    'EGRESOS': 'Egresos Bs.',
    'MONTO': 'Monto Bs.'
}

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Dashboard Ventas Tienda Tech", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

engine = neon_connection.connect()

def renombrar_columnas_para_vista(df, columnas_traducidas):
    return df.rename(columns=columnas_traducidas)


def getventas(mes, gestion):
    return pd.read_sql(
        f"SELECT * FROM produccion WHERE EXTRACT(MONTH FROM fecha) = {mes} AND EXTRACT(YEAR FROM fecha) = {gestion};",
        engine)

def getgastos(mes, gestion):
    dfg = pd.read_sql(
        f"SELECT fecha, monto FROM egresos WHERE EXTRACT(MONTH FROM fecha) = {mes} AND EXTRACT(YEAR FROM fecha) = {gestion};",
        engine)
    # Asegurarse de que 'fecha' esté en formato datetime
    dfg['fecha'] = pd.to_datetime(dfg['fecha'])

    # Ordenar por fecha
    dfg = dfg.sort_values('fecha').reset_index(drop=True)

    # Obtener la semana ISO y el año ISO
    dfg['semana_iso'] = dfg['fecha'].dt.isocalendar().week
    dfg['anio_iso'] = dfg['fecha'].dt.isocalendar().year

    # Crear una lista única de semanas ISO que tienen al menos un día en abril
    semanas_unicas = dfg[['semana_iso', 'anio_iso']].drop_duplicates().sort_values(['anio_iso', 'semana_iso']).reset_index(drop=True)
    semanas_unicas['semana_mes'] = semanas_unicas.index + 1  # Semana 1, 2, ...

    # Unir con el DataFrame original para agregar 'SEMANA N'
    dfg = dfg.merge(semanas_unicas, on=['semana_iso', 'anio_iso'], how='left')
    dfg['rango_semana'] = 'SEMANA ' + dfg['semana_mes'].astype(str)

    # Agrupar por semana
    semanal = dfg.groupby('rango_semana').agg({
        'monto': 'sum'
    }).reset_index()

    # Renombrar columnas finales
    semanal = semanal.rename(columns={
        'rango_semana': 'SEMANA',
        'monto': 'Monto'
    })

    # Total del mes
    totales = semanal[['Monto']].sum().to_frame().T
    totales.insert(0, 'SEMANA', 'TOTAL MES')

    # Concatenar
    return pd.concat([semanal, totales], ignore_index=True)
    

    

def mostrargrid(df):
    # Asegurarse de que 'fecha' esté en formato datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Ordenar por fecha
    df = df.sort_values('fecha').reset_index(drop=True)

    # Obtener la semana ISO y el año ISO
    df['semana_iso'] = df['fecha'].dt.isocalendar().week
    df['anio_iso'] = df['fecha'].dt.isocalendar().year

    # Crear una lista única de semanas ISO que tienen al menos un día en abril
    semanas_unicas = df[['semana_iso', 'anio_iso']].drop_duplicates().sort_values(['anio_iso', 'semana_iso']).reset_index(drop=True)
    semanas_unicas['semana_mes'] = semanas_unicas.index + 1  # Semana 1, 2, ...

    # Unir con el DataFrame original para agregar 'SEMANA N'
    df = df.merge(semanas_unicas, on=['semana_iso', 'anio_iso'], how='left')
    df['rango_semana'] = 'SEMANA ' + df['semana_mes'].astype(str)

    # Agrupar por semana
    semanal = df.groupby('rango_semana').agg({
        'cantidadproducida': 'sum',
        'cantidadcomercializada': 'sum',
        'importe': 'sum',
        'importetotal': 'max',
        'saldoalmacen': 'last'
    }).reset_index()

    # Renombrar columnas finales
    semanal = semanal.rename(columns={
        'rango_semana': 'SEMANA',
        'cantidadproducida': 'PRODUCCION',
        'cantidadcomercializada': 'KGCOMERCIALIZACION',
        'importe': 'BSCOMERCIALIZACION',
        'importetotal': 'INGRESOS',
        'saldoalmacen': 'SALDOALMACENES'
    })

    # Total del mes
    totales = semanal[['PRODUCCION', 'KGCOMERCIALIZACION', 'BSCOMERCIALIZACION', 'INGRESOS', 'SALDOALMACENES']].sum().to_frame().T
    totales.insert(0, 'SEMANA', 'TOTAL MES')

    # Concatenar
    return pd.concat([semanal, totales], ignore_index=True)


with st.sidebar:
    # Filtro de años
    parAno=st.selectbox('Año',options=[2023, 2024, 2025],index=0)
    # Filtro de Mes    
    parMes = st.selectbox('Mes',options=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],index=0)
    
    meses_dict = {
    'Enero': 1,
    'Febrero': 2,
    'Marzo': 3,
    'Abril': 4,
    'Mayo': 5,
    'Junio': 6,
    'Julio': 7,
    'Agosto': 8,
    'Septiembre': 9,
    'Octubre': 10,
    'Noviembre': 11,
    'Diciembre': 12
}

    mes_numero = meses_dict[parMes]
    
    df = getventas(mes_numero,parAno) 
    dfg = getgastos(mes_numero,parAno)   

gridventas = mostrargrid(df)

c1, c2 = st.columns([1, 1])

with c1:
    st.write("### Detalle semanal")
    st.dataframe(gridventas, use_container_width=True)
    # Relleno visual para emparejar altura
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

with c2:
    df_grafico = gridventas[gridventas['SEMANA'] != 'TOTAL MES']

    fig = px.bar(
        df_grafico,
        x='SEMANA',
        y='PRODUCCION',
        title=f'Producción: {parMes} {parAno}',
        text_auto='.2s',
        color_discrete_sequence=["#0D7714"]
    )

    st.plotly_chart(fig, use_container_width=True)
    
df_vista2 = gridventas.rename(columns={
    'SEMANA': 'Detalle Semanal',
    'KGCOMERCIALIZACION': 'Comercialización Kg.',
    'BSCOMERCIALIZACION': 'Comercialización Bs.'
})
c3, c4, c5 = st.columns([1, 1,1], gap="medium")

with c3:
    st.write(f"### Comercializacion ")
    st.dataframe(df_vista2, use_container_width=True)
    # Relleno visual para emparejar altura
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

with c4:

    fig = px.bar(
        df_vista2,
        x='Detalle Semanal',
        y='Comercialización Kg.',
        title=f'Comercializacion en Kgs: {parMes} {parAno}',
        text_auto='.2s',
        color_discrete_sequence=["#781fb4"]
    )

    st.plotly_chart(fig, use_container_width=True)    

with c5:

    fig = px.bar(
        df_vista2,
        x='Detalle Semanal',
        y='Comercialización Bs.',
        title=f'Comercializacion en Bs: {parMes} {parAno}',
        text_auto='.2s',
        color_discrete_sequence=['#1f77b4']
    )

    st.plotly_chart(fig, use_container_width=True)        

    
dfig = gridventas[['SEMANA', 'BSCOMERCIALIZACION']].merge(
    dfg[['SEMANA', 'Monto']],
    on='SEMANA',
    how='inner'  # O 'left' si quieres mantener todas las semanas del df original
)   


df_vista = dfig.rename(columns={
    'SEMANA': 'Detalle Semanal',
    'BSCOMERCIALIZACION': 'Ingresos',
    'Monto': 'Gastos'})  


c6, c7 = st.columns([1,1], gap="medium") 
with c6: 
    st.write(f"### Ingresos - Gastos ")
    st.dataframe(dfig, use_container_width=True)
    # Relleno visual para emparejar altura
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

with c7:
    df_grafico = df_vista[df_vista['Detalle Semanal'] != 'TOTAL MES']
    fig = px.bar(
        df_grafico,
        x='Detalle Semanal',
        y=['Ingresos', 'Gastos'],
        title=f'Ingresos - Gastos: {parMes} {parAno}',
        text_auto='.2s',
        barmode='group',  # Esto coloca las barras lado a lado
        color_discrete_sequence=["#4CAF50", "#F44336"]  # Verde para Ingresos, Rojo para Gastos
    )

    # Personalizar leyenda y ejes
    fig.update_layout(
        legend_title_text='Ingresos - Egresos',
        yaxis_title='Monto',
        xaxis_title='Semana'
    )

    st.plotly_chart(fig, use_container_width=True)    
    