import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import load_all_data

def run():
    """
    Módulo que muestra la tabla con el conteo total de tipos de contrato,
    combinando datos de las tablas Manipuladoras y Planta, con filtros en la barra lateral.
    """
    # Primero, intentemos mostrar algo en la barra lateral para depurar
    st.sidebar.markdown("## Filtros de Depuración")
    st.sidebar.info("Si puedes ver este mensaje, la barra lateral está funcionando correctamente.")
    
    # Filtro simple de prueba
    option = st.sidebar.selectbox(
        'Selecciona una opción de prueba:',
        ['ACTIVO', 'RETIRADO', 'CASO ESPECIAL']
    )
    
    st.sidebar.write(f"Opción seleccionada: {option}")
    
    # Añadir un separador visual
    st.sidebar.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']

    # Verificar columnas disponibles para depuración
    st.subheader("Columnas disponibles en los datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Columnas en Manipuladoras:")
        if not manipuladoras_df.empty:
            st.write(list(manipuladoras_df.columns))
        else:
            st.error("No hay datos en Manipuladoras")
    
    with col2:
        st.write("Columnas en Planta:")
        if not planta_df.empty:
            st.write(list(planta_df.columns))
        else:
            st.error("No hay datos en Planta")
    
    # Verificar que existan las columnas de interés
    if 'tipo_contrato' not in manipuladoras_df.columns:
        if 'TIPO DE CONTRATO' in manipuladoras_df.columns:
            manipuladoras_df['tipo_contrato'] = manipuladoras_df['TIPO DE CONTRATO']
            st.success("Se encontró y normalizó 'TIPO DE CONTRATO' en Manipuladoras")
        else:
            st.error("No se encontró la columna de tipo de contrato en la tabla Manipuladoras")
            return
        
    if 'tipo_contrato' not in planta_df.columns:
        if 'TIPO DE CONTRATO' in planta_df.columns:
            planta_df['tipo_contrato'] = planta_df['TIPO DE CONTRATO']
            st.success("Se encontró y normalizó 'TIPO DE CONTRATO' en Planta")
        else:
            st.error("No se encontró la columna de tipo de contrato en la tabla Planta")
            return
    
    # Verificar columnas de tipo de novedad
    st.subheader("Verificando columnas de tipo de novedad")
    
    if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in manipuladoras_df.columns:
        st.success("Columna 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' encontrada en Manipuladoras")
        # Mostrar valores únicos
        unique_values = manipuladoras_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)'].dropna().unique()
        st.write("Valores únicos:", list(unique_values))
    else:
        st.error("No se encontró la columna 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' en Manipuladoras")
    
    if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in planta_df.columns:
        st.success("Columna 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' encontrada en Planta")
        # Mostrar valores únicos
        unique_values = planta_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)'].dropna().unique()
        st.write("Valores únicos:", list(unique_values))
    else:
        st.error("No se encontró la columna 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' en Planta")
    
    # Combinar los tipos de contrato de ambas fuentes
    tipos_contrato_manipuladoras = manipuladoras_df['tipo_contrato'].dropna()
    tipos_contrato_planta = planta_df['tipo_contrato'].dropna()
    
    # Concatenar las series
    todos_tipos_contrato = pd.concat([tipos_contrato_manipuladoras, tipos_contrato_planta])
    
    # Contar los valores y ordenar por frecuencia descendente
    conteo_tipos = todos_tipos_contrato.value_counts().reset_index()
    conteo_tipos.columns = ['Tipo de Contrato', 'Total']
    
    # Mostrar solo la tabla con los conteos
    st.header("Conteo Total de Tipos de Contrato")
    st.dataframe(conteo_tipos, use_container_width=True)