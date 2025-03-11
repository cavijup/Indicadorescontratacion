import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data
from utils import load_all_data, filter_by_date_range

def run():
    """
    Muestra el análisis y visualización de los tipos de contratos
    de las tres hojas del libro de Google Sheets.
    """
    st.title("Análisis de Tipos de Contratos")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']
        aprendices_df = data_dict['aprendices']

    # Añadir filtro por rango de fechas
    st.sidebar.header("Filtrar por fecha de ingreso")

    # Determinar las fechas mínima y máxima entre todos los DataFrames
    min_dates = []
    max_dates = []

    for df_name, df in [("Manipuladoras", manipuladoras_df), ("Planta", planta_df), ("Aprendices", aprendices_df)]:
        if not df.empty and 'fecha_ingreso' in df.columns:
            # Eliminar valores nulos antes de obtener min/max
            fechas = df['fecha_ingreso'].dropna()
            if not fechas.empty:
                min_dates.append(fechas.min())
                max_dates.append(fechas.max())

    # Establecer fechas mín/máx para los selectores
    if min_dates and max_dates:
        overall_min_date = min(min_dates).date()
        overall_max_date = max(max_dates).date()
        
        # Crear selectores de fecha
        start_date = st.sidebar.date_input("Fecha de inicio", overall_min_date, 
                                        min_value=overall_min_date, 
                                        max_value=overall_max_date)
        end_date = st.sidebar.date_input("Fecha de fin", overall_max_date, 
                                    min_value=overall_min_date, 
                                    max_value=overall_max_date)
        
        # Botón para aplicar filtro
        if st.sidebar.button("Aplicar filtro de fechas"):
            # Aplicar filtro a cada DataFrame
            if not manipuladoras_df.empty and 'fecha_ingreso' in manipuladoras_df.columns:
                manipuladoras_df = filter_by_date_range(manipuladoras_df, pd.Timestamp(start_date), pd.Timestamp(end_date))
            
            if not planta_df.empty and 'fecha_ingreso' in planta_df.columns:
                planta_df = filter_by_date_range(planta_df, pd.Timestamp(start_date), pd.Timestamp(end_date))
            
            if not aprendices_df.empty and 'fecha_ingreso' in aprendices_df.columns:
                aprendices_df = filter_by_date_range(aprendices_df, pd.Timestamp(start_date), pd.Timestamp(end_date))
            
            # Guardar estado del filtro
            st.session_state.filtro_aplicado = True
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            
            st.sidebar.success(f"Filtro aplicado: {start_date} a {end_date}")
        # Mostrar estado del filtro actual
        elif st.session_state.get('filtro_aplicado', False):
            st.sidebar.info(f"Filtro actual: {st.session_state.start_date} a {st.session_state.end_date}")
            
        # Botón para limpiar filtro
        if st.session_state.get('filtro_aplicado', False):
            if st.sidebar.button("Limpiar filtro"):
                # Volver a cargar los datos originales
                data_dict = load_all_data()
                manipuladoras_df = data_dict['manipuladoras']
                planta_df = data_dict['planta']
                aprendices_df = data_dict['aprendices']
                
                # Limpiar estado del filtro
                st.session_state.filtro_aplicado = False
                if 'start_date' in st.session_state:
                    del st.session_state.start_date
                if 'end_date' in st.session_state:
                    del st.session_state.end_date
                
                st.sidebar.success("Filtro eliminado. Mostrando todos los datos.")
                st.experimental_rerun()  # Volver a ejecutar la app para actualizar la interfaz
    
       
    # Verificar que las columnas existan
    for df_name, df in [("Manipuladoras", manipuladoras_df), 
                       ("Planta", planta_df), 
                       ("Aprendices", aprendices_df)]:
        if not df.empty and 'tipo_contrato' not in df.columns:
            st.error(f"La columna 'tipo_contrato' no existe en el DataFrame {df_name}")
            st.write(f"Columnas disponibles: {df.columns.tolist()}")
            return
    
    # Análisis de tipos de contrato por fuente
    st.subheader("Distribución de Tipos de Contrato por Fuente")
    
    # Crear un DataFrame combinado para análisis
    tipos_contrato = []
    
    # Procesar cada DataFrame si tiene datos
    if not manipuladoras_df.empty and 'tipo_contrato' in manipuladoras_df.columns:
        conteo_manipuladoras = manipuladoras_df['tipo_contrato'].value_counts().reset_index()
        conteo_manipuladoras.columns = ['tipo_contrato', 'conteo']
        conteo_manipuladoras['fuente'] = 'Manipuladoras'
        tipos_contrato.append(conteo_manipuladoras)
    
    if not planta_df.empty and 'tipo_contrato' in planta_df.columns:
        conteo_planta = planta_df['tipo_contrato'].value_counts().reset_index()
        conteo_planta.columns = ['tipo_contrato', 'conteo']
        conteo_planta['fuente'] = 'Planta'
        tipos_contrato.append(conteo_planta)
    
    if not aprendices_df.empty and 'tipo_contrato' in aprendices_df.columns:
        conteo_aprendices = aprendices_df['tipo_contrato'].value_counts().reset_index()
        conteo_aprendices.columns = ['tipo_contrato', 'conteo']
        conteo_aprendices['fuente'] = 'Aprendices'
        tipos_contrato.append(conteo_aprendices)
    
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
    else:
        st.warning("No hay datos suficientes para analizar los tipos de contrato.")
    
    # Gráfico de torta para distribución total de contratos
    st.subheader("Distribución Total de Tipos de Contrato")
    
    if tipos_contrato:
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
    
    # Análisis adicional - Tendencia de contratación por tipo
    st.subheader("Análisis Temporal de Contratos")
    st.info("Este análisis muestra la distribución de contratos por fecha de ingreso, si los datos de fecha están disponibles.")
    
    # Preparar datos para análisis temporal
    dfs_with_dates = []
    
    # Añadir cada DataFrame si contiene fechas válidas
    if 'fecha_ingreso' in manipuladoras_df.columns and 'tipo_contrato' in manipuladoras_df.columns:
        fecha_manipuladoras = manipuladoras_df[['fecha_ingreso', 'tipo_contrato']].copy()
        fecha_manipuladoras['fuente'] = 'Manipuladoras'
        dfs_with_dates.append(fecha_manipuladoras)
    
    if 'fecha_ingreso' in planta_df.columns and 'tipo_contrato' in planta_df.columns:
        fecha_planta = planta_df[['fecha_ingreso', 'tipo_contrato']].copy()
        fecha_planta['fuente'] = 'Planta'
        dfs_with_dates.append(fecha_planta)
    
    if 'fecha_ingreso' in aprendices_df.columns and 'tipo_contrato' in aprendices_df.columns:
        fecha_aprendices = aprendices_df[['fecha_ingreso', 'tipo_contrato']].copy()
        fecha_aprendices['fuente'] = 'Aprendices'
        dfs_with_dates.append(fecha_aprendices)
    
    if dfs_with_dates:
        # Combinar todos los DataFrames con fechas
        combined_dates = pd.concat(dfs_with_dates, ignore_index=True)
        
        # Filtrar filas con fechas nulas
        combined_dates = combined_dates.dropna(subset=['fecha_ingreso'])
        
        if not combined_dates.empty:
            # Extraer año y mes para agrupar
            combined_dates['año_mes'] = combined_dates['fecha_ingreso'].dt.to_period('M')
            
            # Agrupar por año-mes y tipo de contrato
            temporal_data = combined_dates.groupby(['año_mes', 'tipo_contrato']).size().reset_index(name='conteo')
            temporal_data['año_mes'] = temporal_data['año_mes'].astype(str)
            
            # Crear gráfico de líneas
            fig_line = px.line(
                temporal_data, 
                x='año_mes', 
                y='conteo', 
                color='tipo_contrato',
                markers=True,
                title='Tendencia de Contratos por Tipo a lo Largo del Tiempo',
                labels={'año_mes': 'Año-Mes', 'conteo': 'Cantidad', 'tipo_contrato': 'Tipo de Contrato'}
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("No hay fechas válidas para realizar análisis temporal.")
    else:
        st.warning("No hay datos de fechas disponibles para realizar análisis temporal.")