import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_all_data

def run():
    """
    Módulo que muestra los indicadores de tipos de contrato
    de las tablas Manipuladoras y Planta.
    """
    st.title("Indicadores de Tipos de Contrato")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']

    # Verificar que existan las columnas de interés
    if 'tipo_contrato' not in manipuladoras_df.columns:
        st.error("No se encontró la columna 'tipo_contrato' en la tabla Manipuladoras")
        st.write("Columnas disponibles:", manipuladoras_df.columns.tolist())
        return
        
    if 'tipo_contrato' not in planta_df.columns:
        st.error("No se encontró la columna 'tipo_contrato' en la tabla Planta")
        st.write("Columnas disponibles:", planta_df.columns.tolist())
        return
    
    # Crear conteos de tipos de contrato para cada fuente
    conteo_manipuladoras = manipuladoras_df['tipo_contrato'].value_counts().reset_index()
    conteo_manipuladoras.columns = ['Tipo de Contrato', 'Cantidad']
    conteo_manipuladoras['Fuente'] = 'Manipuladoras'
    
    conteo_planta = planta_df['tipo_contrato'].value_counts().reset_index()
    conteo_planta.columns = ['Tipo de Contrato', 'Cantidad']
    conteo_planta['Fuente'] = 'Planta'
    
    # Combinar ambos conteos
    df_combinado = pd.concat([conteo_manipuladoras, conteo_planta], ignore_index=True)
    
    # Calcular totales por tipo de contrato
    totales = df_combinado.groupby('Tipo de Contrato')['Cantidad'].sum().reset_index()
    totales['Fuente'] = 'Total'
    
    # Agregar los totales al DataFrame combinado
    df_final = pd.concat([df_combinado, totales], ignore_index=True)
    
    # Crear tabla pivot para mejor visualización
    pivot_table = df_final.pivot(index='Tipo de Contrato', columns='Fuente', values='Cantidad')
    pivot_table = pivot_table.fillna(0).astype(int)
    
    # Reordenar columnas para que 'Total' sea la última
    if 'Total' in pivot_table.columns:
        cols = [col for col in pivot_table.columns if col != 'Total'] + ['Total']
        pivot_table = pivot_table[cols]
    
    # Mostrar la tabla
    st.subheader("Conteo de Tipos de Contrato por Fuente")
    st.dataframe(pivot_table, use_container_width=True)
    
    # Crear gráfico de barras
    st.subheader("Visualización de Tipos de Contrato")
    
    fig = px.bar(
        df_combinado,
        x='Tipo de Contrato',
        y='Cantidad',
        color='Fuente',
        title='Distribución de Tipos de Contrato',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de torta para cada fuente
    st.subheader("Distribución Porcentual por Fuente")
    
    # Usar pestañas para separar los gráficos
    tab1, tab2 = st.tabs(["Manipuladoras", "Planta"])
    
    with tab1:
        fig_pie1 = px.pie(
            conteo_manipuladoras,
            values='Cantidad',
            names='Tipo de Contrato',
            title='Distribución de Tipos de Contrato - Manipuladoras',
            hole=0.4
        )
        st.plotly_chart(fig_pie1, use_container_width=True)
    
    with tab2:
        fig_pie2 = px.pie(
            conteo_planta,
            values='Cantidad',
            names='Tipo de Contrato',
            title='Distribución de Tipos de Contrato - Planta',
            hole=0.4
        )
        st.plotly_chart(fig_pie2, use_container_width=True)