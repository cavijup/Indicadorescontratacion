import streamlit as st
import pandas as pd
from utils import load_all_data

def run():
    """
    Módulo que muestra una tabla simple con el conteo total de tipos de contrato,
    combinando datos de las tablas Manipuladoras y Planta.
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
        if 'TIPO DE CONTRATO' in manipuladoras_df.columns:
            manipuladoras_df['tipo_contrato'] = manipuladoras_df['TIPO DE CONTRATO']
            st.success("Se encontró 'TIPO DE CONTRATO' y se ha mapeado correctamente.")
        else:
            return
        
    if 'tipo_contrato' not in planta_df.columns:
        st.error("No se encontró la columna 'tipo_contrato' en la tabla Planta")
        st.write("Columnas disponibles:", planta_df.columns.tolist())
        if 'TIPO DE CONTRATO' in planta_df.columns:
            planta_df['tipo_contrato'] = planta_df['TIPO DE CONTRATO']
            st.success("Se encontró 'TIPO DE CONTRATO' y se ha mapeado correctamente.")
        else:
            return
    
    # Combinar los tipos de contrato de ambas fuentes
    tipos_contrato_manipuladoras = manipuladoras_df['tipo_contrato'].dropna()
    tipos_contrato_planta = planta_df['tipo_contrato'].dropna()
    
    # Concatenar las series
    todos_tipos_contrato = pd.concat([tipos_contrato_manipuladoras, tipos_contrato_planta])
    
    # Contar los valores y ordenar por frecuencia descendente
    conteo_tipos = todos_tipos_contrato.value_counts().reset_index()
    conteo_tipos.columns = ['Tipo de Contrato', 'Total']
    
    # Mostrar la tabla simple con los conteos
    st.subheader("Conteo Total de Tipos de Contrato")
    st.dataframe(conteo_tipos, use_container_width=True)