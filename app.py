import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_all_data

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Indicadores de Contratación",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Función principal que ejecuta la aplicación"""
    
    # Título y descripción
    st.title("Dashboard de Indicadores de Contratación")
    st.markdown("Análisis de datos de contratación para Planta y Manipuladoras")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']
    
    # Verificar que los datos se hayan cargado correctamente
    if manipuladoras_df.empty or planta_df.empty:
        st.error("No se pudieron cargar los datos. Por favor verifica la conexión con Google Sheets.")
        return

    # Mostrar indicador: Número de personas por tipo de contrato
    st.header("Número de personas por tipo de contrato")
    
    # Asegurarse de que las columnas existen
    if 'TIPO DE CONTRATO' not in planta_df.columns:
        st.error("La columna 'TIPO DE CONTRATO' no se encontró en la tabla Planta.")
        st.write(f"Columnas disponibles en Planta: {planta_df.columns.tolist()}")
    
    if 'TIPO DE CONTRATO' not in manipuladoras_df.columns:
        st.error("La columna 'TIPO DE CONTRATO' no se encontró en la tabla Manipuladoras.")
        st.write(f"Columnas disponibles en Manipuladoras: {manipuladoras_df.columns.tolist()}")
    
    # Crear DataFrames combinados para el análisis
    tipos_contrato = []
    
    # Procesar datos de Planta
    if 'TIPO DE CONTRATO' in planta_df.columns and not planta_df.empty:
        conteo_planta = planta_df['TIPO DE CONTRATO'].value_counts().reset_index()
        conteo_planta.columns = ['tipo_contrato', 'conteo']
        conteo_planta['fuente'] = 'Planta'
        tipos_contrato.append(conteo_planta)
    
    # Procesar datos de Manipuladoras
    if 'TIPO DE CONTRATO' in manipuladoras_df.columns and not manipuladoras_df.empty:
        conteo_manipuladoras = manipuladoras_df['TIPO DE CONTRATO'].value_counts().reset_index()
        conteo_manipuladoras.columns = ['tipo_contrato', 'conteo']
        conteo_manipuladoras['fuente'] = 'Manipuladoras'
        tipos_contrato.append(conteo_manipuladoras)
    
    # Combinar todos los conteos
    if tipos_contrato:
        df_tipos_contrato = pd.concat(tipos_contrato, ignore_index=True)
        
        # Crear gráfico de barras
        fig = px.bar(
            df_tipos_contrato, 
            x='tipo_contrato', 
            y='conteo', 
            color='fuente',
            title='Distribución de Tipos de Contrato por Fuente',
            labels={'tipo_contrato': 'Tipo de Contrato', 'conteo': 'Cantidad', 'fuente': 'Fuente'},
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla de datos
        st.subheader("Tabla de Datos - Tipos de Contrato")
        st.dataframe(df_tipos_contrato)
        
        # Gráfico de torta para distribución total de contratos
        st.subheader("Distribución Total de Tipos de Contrato")
        
        # Agrupar por tipo de contrato para obtener el total general
        total_contratos = df_tipos_contrato.groupby('tipo_contrato')['conteo'].sum().reset_index()
        
        fig_pie = px.pie(
            total_contratos, 
            values='conteo', 
            names='tipo_contrato',
            title='Distribución Total de Tipos de Contrato',
            hole=0.4
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Mostrar métricas
        st.subheader("Resumen Numérico")
        col1, col2 = st.columns(2)
        
        with col1:
            planta_total = df_tipos_contrato[df_tipos_contrato['fuente'] == 'Planta']['conteo'].sum()
            st.metric("Total Planta", f"{planta_total}")
        
        with col2:
            manipuladoras_total = df_tipos_contrato[df_tipos_contrato['fuente'] == 'Manipuladoras']['conteo'].sum()
            st.metric("Total Manipuladoras", f"{manipuladoras_total}")
        
        st.metric("Total General", f"{planta_total + manipuladoras_total}")
    else:
        st.warning("No hay datos suficientes para mostrar el indicador de tipos de contrato.")

if __name__ == "__main__":
    main()