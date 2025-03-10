import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data
from utils import load_all_data, filter_by_date_range

def run():
    """
    Muestra el análisis y visualización de los tipos de novedades
    de las tres hojas del libro de Google Sheets.
    """
    st.title("Análisis de Tipos de Novedades")
    
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

    
    # Mostrar indicadores de novedades
    st.subheader("Resumen de Tipos de Novedades")
    
    # Procesamiento para Manipuladoras
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Manipuladoras")
        if 'tipo_novedad' in manipuladoras_df.columns and not manipuladoras_df.empty:
            tipo_novedad_manipuladoras = manipuladoras_df['tipo_novedad'].value_counts()
            
            # Mostrar conteo total
            total_manipuladoras = tipo_novedad_manipuladoras.sum()
            st.metric("Total de registros", f"{total_manipuladoras}")
            
            # Mostrar desglose por tipo de novedad
            for novedad, count in tipo_novedad_manipuladoras.items():
                st.metric(f"{novedad}", f"{count} ({count/total_manipuladoras:.1%})")
        else:
            st.warning("No hay datos de tipos de novedad para Manipuladoras")
    
    with col2:
        st.markdown("### Planta")
        if 'tipo_novedad' in planta_df.columns and not planta_df.empty:
            tipo_novedad_planta = planta_df['tipo_novedad'].value_counts()
            
            # Mostrar conteo total
            total_planta = tipo_novedad_planta.sum()
            st.metric("Total de registros", f"{total_planta}")
            
            # Mostrar desglose por tipo de novedad
            for novedad, count in tipo_novedad_planta.items():
                st.metric(f"{novedad}", f"{count} ({count/total_planta:.1%})")
        else:
            st.warning("No hay datos de tipos de novedad para Planta")
    
    with col3:
        st.markdown("### Aprendices")
        if 'tipo_novedad' in aprendices_df.columns and not aprendices_df.empty:
            tipo_novedad_aprendices = aprendices_df['tipo_novedad'].value_counts()
            
            # Mostrar conteo total
            total_aprendices = tipo_novedad_aprendices.sum()
            st.metric("Total de registros", f"{total_aprendices}")
            
            # Mostrar desglose por tipo de novedad
            for novedad, count in tipo_novedad_aprendices.items():
                st.metric(f"{novedad}", f"{count} ({count/total_aprendices:.1%})")
        else:
            st.warning("No hay datos de tipos de novedad para Aprendices")
    
    # Análisis comparativo de novedades
    st.subheader("Comparativa de Tipos de Novedad por Fuente")
    
    # Preparar datos para el gráfico comparativo
    novedades_data = []
    
    # Procesar cada DataFrame si tiene datos de novedad
    if 'tipo_novedad' in manipuladoras_df.columns and not manipuladoras_df.empty:
        novedad_manipuladoras = manipuladoras_df['tipo_novedad'].value_counts().reset_index()
        novedad_manipuladoras.columns = ['tipo_novedad', 'conteo']
        novedad_manipuladoras['fuente'] = 'Manipuladoras'
        novedades_data.append(novedad_manipuladoras)
    
    if 'tipo_novedad' in planta_df.columns and not planta_df.empty:
        novedad_planta = planta_df['tipo_novedad'].value_counts().reset_index()
        novedad_planta.columns = ['tipo_novedad', 'conteo']
        novedad_planta['fuente'] = 'Planta'
        novedades_data.append(novedad_planta)
    
    if 'tipo_novedad' in aprendices_df.columns and not aprendices_df.empty:
        novedad_aprendices = aprendices_df['tipo_novedad'].value_counts().reset_index()
        novedad_aprendices.columns = ['tipo_novedad', 'conteo']
        novedad_aprendices['fuente'] = 'Aprendices'
        novedades_data.append(novedad_aprendices)
    
    if novedades_data:
        # Combinar todos los datos de novedades
        novedades_combined = pd.concat(novedades_data, ignore_index=True)
        
        # Crear gráfico de barras para comparativa
        fig = px.bar(
            novedades_combined,
            x='tipo_novedad',
            y='conteo',
            color='fuente',
            title='Comparativa de Tipos de Novedad por Fuente',
            labels={'tipo_novedad': 'Tipo de Novedad', 'conteo': 'Cantidad', 'fuente': 'Fuente'},
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla de datos
        st.subheader("Tabla de Datos - Tipos de Novedad")
        st.dataframe(novedades_combined)
        
        # Gráfico de torta para distribución total de novedades
        st.subheader("Distribución Total de Tipos de Novedad")
        
        # Agrupar por tipo de novedad para obtener el total general
        total_novedades = novedades_combined.groupby('tipo_novedad')['conteo'].sum().reset_index()
        
        fig_pie = px.pie(
            total_novedades,
            values='conteo',
            names='tipo_novedad',
            title='Distribución Total de Tipos de Novedad',
            hole=0.4
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para mostrar la comparativa de tipos de novedad.")
    
    # Análisis cruzado: Tipos de Contrato por Tipo de Novedad
    st.subheader("Análisis Cruzado: Tipos de Contrato por Tipo de Novedad")
    
    # Verificar primero si existen todas las columnas necesarias
    has_cross_data = False
    
    if 'tipo_novedad' in manipuladoras_df.columns and 'tipo_contrato' in manipuladoras_df.columns and not manipuladoras_df.empty:
        has_cross_data = True
    if 'tipo_novedad' in planta_df.columns and 'tipo_contrato' in planta_df.columns and not planta_df.empty:
        has_cross_data = True
    if 'tipo_novedad' in aprendices_df.columns and 'tipo_contrato' in aprendices_df.columns and not aprendices_df.empty:
        has_cross_data = True
    
    if not has_cross_data:
        st.warning("No se encuentran las columnas necesarias para el análisis cruzado.")
        return
        
    # Preparar datos para el análisis cruzado
    cross_data = []
    
    # Manipuladoras
    if 'tipo_novedad' in manipuladoras_df.columns and 'tipo_contrato' in manipuladoras_df.columns and not manipuladoras_df.empty:
        cross_manipuladoras = manipuladoras_df.groupby(['tipo_novedad', 'tipo_contrato']).size().reset_index(name='conteo')
        cross_manipuladoras['fuente'] = 'Manipuladoras'
        cross_data.append(cross_manipuladoras)
    
    # Planta
    if 'tipo_novedad' in planta_df.columns and 'tipo_contrato' in planta_df.columns and not planta_df.empty:
        cross_planta = planta_df.groupby(['tipo_novedad', 'tipo_contrato']).size().reset_index(name='conteo')
        cross_planta['fuente'] = 'Planta'
        cross_data.append(cross_planta)
    
    # Aprendices
    if 'tipo_novedad' in aprendices_df.columns and 'tipo_contrato' in aprendices_df.columns and not aprendices_df.empty:
        cross_aprendices = aprendices_df.groupby(['tipo_novedad', 'tipo_contrato']).size().reset_index(name='conteo')
        cross_aprendices['fuente'] = 'Aprendices'
        cross_data.append(cross_aprendices)
    
    if cross_data:
        # Combinar todos los datos cruzados
        cross_combined = pd.concat(cross_data, ignore_index=True)
        
        # Crear un gráfico de barras apiladas
        fig_cross = px.bar(
            cross_combined,
            x='tipo_novedad',
            y='conteo',
            color='tipo_contrato',
            facet_col='fuente',
            title='Distribución de Contratos por Tipo de Novedad',
            labels={'tipo_novedad': 'Tipo de Novedad', 'conteo': 'Cantidad', 'tipo_contrato': 'Tipo de Contrato'}
        )
        
        # Ajustar el layout para mejor visualización
        fig_cross.update_layout(height=500)
        
        st.plotly_chart(fig_cross, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para realizar el análisis cruzado.")
    
    # Análisis específico para registros con BUGA en el área (Planta)
    st.subheader("Análisis Específico - Área BUGA (Planta)")

    # Verificar si la columna AREA existe en el DataFrame de Planta
    if 'AREA' in planta_df.columns and not planta_df.empty:
        # Filtrar registros que contengan 'BUGA' en la columna AREA
        buga_df = planta_df[planta_df['AREA'].str.contains('BUGA', case=False, na=False)]
        
        if not buga_df.empty:
            # Conteo de tipos de novedad para registros BUGA
            buga_novedad_counts = buga_df['tipo_novedad'].value_counts().reset_index()
            buga_novedad_counts.columns = ['tipo_novedad', 'conteo']
            
            # Calcular porcentajes
            total_buga = buga_novedad_counts['conteo'].sum()
            buga_novedad_counts['porcentaje'] = (buga_novedad_counts['conteo'] / total_buga * 100).round(1)
            
            # Mostrar métricas
            st.metric("Total registros BUGA", f"{total_buga}")
            
            # Mostrar distribución en columnas
            cols = st.columns(len(buga_novedad_counts))
            for i, (_, row) in enumerate(buga_novedad_counts.iterrows()):
                with cols[i]:
                    st.metric(
                        f"{row['tipo_novedad']}", 
                        f"{row['conteo']}", 
                        f"{row['porcentaje']}%"
                    )
            
            # Crear gráfico de torta para distribución
            fig_buga_pie = px.pie(
                buga_novedad_counts,
                values='conteo',
                names='tipo_novedad',
                title='Distribución de Tipos de Novedad - Área BUGA',
                hole=0.4
            )
            st.plotly_chart(fig_buga_pie, use_container_width=True)
            
            # Análisis cruzado de BUGA: Tipos de Contrato por Tipo de Novedad
            if 'tipo_contrato' in buga_df.columns:
                st.subheader("BUGA - Tipos de Contrato por Tipo de Novedad")
                
                # Agrupar por tipo de novedad y tipo de contrato
                buga_cross = buga_df.groupby(['tipo_novedad', 'tipo_contrato']).size().reset_index(name='conteo')
                
                # Crear gráfico de barras apiladas
                fig_buga_cross = px.bar(
                    buga_cross,
                    x='tipo_novedad',
                    y='conteo',
                    color='tipo_contrato',
                    title='BUGA - Distribución de Contratos por Tipo de Novedad',
                    labels={'tipo_novedad': 'Tipo de Novedad', 'conteo': 'Cantidad', 'tipo_contrato': 'Tipo de Contrato'}
                )
                
                st.plotly_chart(fig_buga_cross, use_container_width=True)
                
                # Mostrar tabla de datos para análisis detallado
                st.subheader("Detalle de Registros - Área BUGA")
                st.dataframe(buga_df[['empresa', 'tipo_novedad', 'tipo_contrato', 'fecha_ingreso', 'fecha_retiro']])
        else:
            st.warning("No se encontraron registros con 'BUGA' en el área.")
    else:
        st.warning("La columna 'AREA' no existe en los datos de Planta o no hay datos disponibles.")
        
