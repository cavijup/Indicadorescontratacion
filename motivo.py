import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data, filter_by_date_range, filter_by_novedad, get_all_novedades_types

def run():
    """
    Muestra el análisis y visualización de los motivos de retiro
    de las tablas de Planta y Manipuladoras.
    """
    st.title("Análisis de Motivos de Retiro")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']
        aprendices_df = data_dict['aprendices']  # No se usará para el análisis de motivos

    # Obtener todos los tipos de novedad disponibles
    all_novedades = get_all_novedades_types(data_dict)

    # Añadir filtro por tipo de novedad
    st.sidebar.header("Filtrar por tipo de novedad")
    
    # Selector de tipos de novedad
    selected_novedades = st.sidebar.multiselect(
        "Seleccionar tipos de novedad",
        options=all_novedades,
        default=all_novedades  # Por defecto, todos seleccionados
    )
    
    # Botón para aplicar filtro de novedad
    if st.sidebar.button("Aplicar filtro de novedad"):
        # Aplicar filtro a cada DataFrame
        if not manipuladoras_df.empty and 'tipo_novedad' in manipuladoras_df.columns:
            manipuladoras_df = filter_by_novedad(manipuladoras_df, selected_novedades)
        
        if not planta_df.empty and 'tipo_novedad' in planta_df.columns:
            planta_df = filter_by_novedad(planta_df, selected_novedades)
        
        # Guardar estado del filtro
        st.session_state.novedad_filtro_aplicado = True
        st.session_state.selected_novedades = selected_novedades
        
        st.sidebar.success(f"Filtro de novedad aplicado: {', '.join(selected_novedades)}")
    
    # Mostrar estado del filtro actual
    elif st.session_state.get('novedad_filtro_aplicado', False):
        st.sidebar.info(f"Filtro de novedad actual: {', '.join(st.session_state.selected_novedades)}")
        
        # Si hay filtro guardado en la sesión, aplicarlo
        if not manipuladoras_df.empty and 'tipo_novedad' in manipuladoras_df.columns:
            manipuladoras_df = filter_by_novedad(manipuladoras_df, st.session_state.selected_novedades)
        
        if not planta_df.empty and 'tipo_novedad' in planta_df.columns:
            planta_df = filter_by_novedad(planta_df, st.session_state.selected_novedades)
    
    # Botón para limpiar filtro de novedad
    if st.session_state.get('novedad_filtro_aplicado', False):
        if st.sidebar.button("Limpiar filtro de novedad"):
            # Volver a cargar los datos originales
            data_dict = load_all_data()
            manipuladoras_df = data_dict['manipuladoras']
            planta_df = data_dict['planta']
            
            # Limpiar estado del filtro
            st.session_state.novedad_filtro_aplicado = False
            if 'selected_novedades' in st.session_state:
                del st.session_state.selected_novedades
            
            st.sidebar.success("Filtro de novedad eliminado. Mostrando todos los tipos de novedad.")
            st.experimental_rerun()  # Volver a ejecutar la app para actualizar la interfaz

    # Añadir filtro por rango de fechas
    st.sidebar.header("Filtrar por fecha de retiro")

    # Determinar las fechas mínima y máxima de retiro entre los DataFrames
    min_dates = []
    max_dates = []

    # Para planta
    if not planta_df.empty and 'fecha_retiro' in planta_df.columns:
        fechas_planta = planta_df['fecha_retiro'].dropna()
        if not fechas_planta.empty:
            min_dates.append(fechas_planta.min())
            max_dates.append(fechas_planta.max())

    # Para manipuladoras
    if not manipuladoras_df.empty and 'fecha_retiro' in manipuladoras_df.columns:
        fechas_manip = manipuladoras_df['fecha_retiro'].dropna()
        if not fechas_manip.empty:
            min_dates.append(fechas_manip.min())
            max_dates.append(fechas_manip.max())

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
        
        # Botón para aplicar filtro de fechas
        if st.sidebar.button("Aplicar filtro de fechas"):
            # Aplicar filtro a cada DataFrame
            if not manipuladoras_df.empty and 'fecha_retiro' in manipuladoras_df.columns:
                manipuladoras_df = filter_by_date_range(manipuladoras_df, pd.Timestamp(start_date), pd.Timestamp(end_date), date_column='fecha_retiro')
            
            if not planta_df.empty and 'fecha_retiro' in planta_df.columns:
                planta_df = filter_by_date_range(planta_df, pd.Timestamp(start_date), pd.Timestamp(end_date), date_column='fecha_retiro')
            
            # Guardar estado del filtro
            st.session_state.filtro_aplicado = True
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            
            st.sidebar.success(f"Filtro de fechas aplicado: {start_date} a {end_date}")
            
        # Mostrar estado del filtro actual
        elif st.session_state.get('filtro_aplicado', False):
            st.sidebar.info(f"Filtro de fechas actual: {st.session_state.start_date} a {st.session_state.end_date}")
            
            # Si hay filtro guardado en la sesión, aplicarlo
            if not manipuladoras_df.empty and 'fecha_retiro' in manipuladoras_df.columns:
                manipuladoras_df = filter_by_date_range(manipuladoras_df, 
                                                       pd.Timestamp(st.session_state.start_date), 
                                                       pd.Timestamp(st.session_state.end_date),
                                                       date_column='fecha_retiro')
            
            if not planta_df.empty and 'fecha_retiro' in planta_df.columns:
                planta_df = filter_by_date_range(planta_df, 
                                               pd.Timestamp(st.session_state.start_date), 
                                               pd.Timestamp(st.session_state.end_date),
                                               date_column='fecha_retiro')
                
        # Botón para limpiar filtro de fechas
        if st.session_state.get('filtro_aplicado', False):
            if st.sidebar.button("Limpiar filtro de fechas"):
                # Volver a cargar los datos originales (pero mantener el filtro de novedad si está activo)
                data_dict = load_all_data()
                manipuladoras_df = data_dict['manipuladoras']
                planta_df = data_dict['planta']
                
                # Aplicar el filtro de novedad si está activo
                if st.session_state.get('novedad_filtro_aplicado', False):
                    if not manipuladoras_df.empty and 'tipo_novedad' in manipuladoras_df.columns:
                        manipuladoras_df = filter_by_novedad(manipuladoras_df, st.session_state.selected_novedades)
                    
                    if not planta_df.empty and 'tipo_novedad' in planta_df.columns:
                        planta_df = filter_by_novedad(planta_df, st.session_state.selected_novedades)
                
                # Limpiar estado del filtro de fechas
                st.session_state.filtro_aplicado = False
                if 'start_date' in st.session_state:
                    del st.session_state.start_date
                if 'end_date' in st.session_state:
                    del st.session_state.end_date
                
                st.sidebar.success("Filtro de fechas eliminado.")
                st.experimental_rerun()  # Volver a ejecutar la app para actualizar la interfaz

    # Analizar los motivos de retiro
    st.subheader("Motivos de Retiro")
    
    # Preparamos las pestañas para los análisis de cada tabla
    tab1, tab2, tab3 = st.tabs(["Resumen General", "Planta", "Manipuladoras"])
    
    # Mapear y estandarizar los nombres de columnas para motivo de retiro
    if 'MOTIVO DEL RETIRO' in planta_df.columns:
        planta_df['motivo_retiro'] = planta_df['MOTIVO DEL RETIRO']
    elif 'motivo_retiro' not in planta_df.columns:
        st.error("No se encontró la columna 'MOTIVO DEL RETIRO' en la tabla Planta")
        planta_df['motivo_retiro'] = None
    
    if 'MOTIVO DEL RETIRO' in manipuladoras_df.columns:
        manipuladoras_df['motivo_retiro'] = manipuladoras_df['MOTIVO DEL RETIRO']
    elif 'motivo_retiro' not in manipuladoras_df.columns:
        st.error("No se encontró la columna 'MOTIVO DEL RETIRO' en la tabla Manipuladoras")
        manipuladoras_df['motivo_retiro'] = None
    
    # Mapear la columna de programa para manipuladoras
    if 'PROGRAMA AL QUE PERTENECE' in manipuladoras_df.columns:
        manipuladoras_df['programa'] = manipuladoras_df['PROGRAMA AL QUE PERTENECE']
    elif 'programa' not in manipuladoras_df.columns:
        manipuladoras_df['programa'] = "No especificado"
    
    # Pestaña 1: Resumen General
    with tab1:
        st.markdown("### Distribución General de Motivos de Retiro")
        
        # Preparar datos combinados
        motivos_data = []
        
        # Procesar motivos de Planta
        if 'motivo_retiro' in planta_df.columns and not planta_df.empty:
            # Filtrar registros con motivo de retiro (no nulos)
            planta_con_motivo = planta_df.dropna(subset=['motivo_retiro'])
            
            if not planta_con_motivo.empty:
                motivos_planta = planta_con_motivo['motivo_retiro'].value_counts().reset_index()
                motivos_planta.columns = ['motivo', 'conteo']
                motivos_planta['fuente'] = 'Planta'
                motivos_data.append(motivos_planta)
        
        # Procesar motivos de Manipuladoras
        if 'motivo_retiro' in manipuladoras_df.columns and not manipuladoras_df.empty:
            # Filtrar registros con motivo de retiro (no nulos)
            manipuladoras_con_motivo = manipuladoras_df.dropna(subset=['motivo_retiro'])
            
            if not manipuladoras_con_motivo.empty:
                motivos_manipuladoras = manipuladoras_con_motivo['motivo_retiro'].value_counts().reset_index()
                motivos_manipuladoras.columns = ['motivo', 'conteo']
                motivos_manipuladoras['fuente'] = 'Manipuladoras'
                motivos_data.append(motivos_manipuladoras)
        
        if motivos_data:
            # Combinar todos los datos de motivos
            motivos_combined = pd.concat(motivos_data, ignore_index=True)
            
            # Agrupar por motivo para obtener el total general
            total_motivos = motivos_combined.groupby('motivo')['conteo'].sum().reset_index().sort_values('conteo', ascending=False)
            
            # Mostrar los 10 motivos más comunes en un gráfico
            top_motivos = total_motivos.head(10)
            
            # Crear gráfico de barras para top motivos
            fig_bar = px.bar(
                top_motivos,
                x='motivo',
                y='conteo',
                title='Top 10 Motivos de Retiro',
                labels={'motivo': 'Motivo', 'conteo': 'Cantidad'},
                color='conteo',
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Crear gráfico de torta para distribución general
            fig_pie = px.pie(
                total_motivos,
                values='conteo',
                names='motivo',
                title='Distribución de Motivos de Retiro',
                hole=0.4
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Gráfico comparativo entre fuentes
            fig_comp = px.bar(
                motivos_combined,
                x='motivo',
                y='conteo',
                color='fuente',
                title='Comparativa de Motivos de Retiro por Fuente',
                labels={'motivo': 'Motivo', 'conteo': 'Cantidad', 'fuente': 'Fuente'},
                barmode='group'
            )
            
            # Ajustar layout para mejor visualización
            fig_comp.update_layout(
                xaxis={'categoryorder':'total descending'},
                height=600
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Mostrar tabla de datos
            st.subheader("Tabla de Datos - Motivos de Retiro")
            st.dataframe(motivos_combined)
        else:
            st.warning("No hay datos de motivos de retiro disponibles para el análisis.")
    
    # Pestaña 2: Análisis Planta
    with tab2:
        st.markdown("### Análisis de Motivos de Retiro - Planta")
        
        if 'motivo_retiro' in planta_df.columns and not planta_df.empty:
            # Filtrar registros con motivo de retiro (no nulos)
            planta_con_motivo = planta_df.dropna(subset=['motivo_retiro'])
            
            if not planta_con_motivo.empty:
                # Análisis de motivos
                motivos_planta = planta_con_motivo['motivo_retiro'].value_counts().reset_index()
                motivos_planta.columns = ['motivo', 'conteo']
                
                # Mostrar métricas
                total_retiros = motivos_planta['conteo'].sum()
                st.metric("Total de registros con motivo de retiro", f"{total_retiros}")
                
                # Gráfico de barras
                fig_planta = px.bar(
                    motivos_planta.head(15),  # Top 15 motivos
                    x='motivo',
                    y='conteo',
                    title='Principales Motivos de Retiro - Planta',
                    labels={'motivo': 'Motivo', 'conteo': 'Cantidad'},
                    color='conteo',
                    color_continuous_scale='Blues'
                )
                
                st.plotly_chart(fig_planta, use_container_width=True)
                
                # Análisis por empresa si está disponible
                if 'empresa' in planta_con_motivo.columns:
                    st.markdown("#### Motivos de Retiro por Empresa")
                    
                    # Agrupar por empresa y motivo
                    empresa_motivo = planta_con_motivo.groupby(['empresa', 'motivo_retiro']).size().reset_index(name='conteo')
                    
                    # Obtener las empresas con más retiros
                    top_empresas = planta_con_motivo['empresa'].value_counts().nlargest(5).index.tolist()
                    
                    # Filtrar para las empresas principales
                    empresa_motivo_top = empresa_motivo[empresa_motivo['empresa'].isin(top_empresas)]
                    
                    # Crear gráfico
                    fig_empresa_motivo = px.bar(
                        empresa_motivo_top,
                        x='motivo_retiro',
                        y='conteo',
                        color='empresa',
                        title='Motivos de Retiro por Empresa Principal',
                        labels={'motivo_retiro': 'Motivo', 'conteo': 'Cantidad', 'empresa': 'Empresa'},
                        barmode='group'
                    )
                    
                    # Ajustar layout
                    fig_empresa_motivo.update_layout(
                        xaxis={'categoryorder':'total descending'},
                        height=500
                    )
                    
                    st.plotly_chart(fig_empresa_motivo, use_container_width=True)
                
                # Mostrar tabla completa de motivos
                st.subheader("Tabla Completa - Motivos de Retiro Planta")
                st.dataframe(motivos_planta)
            else:
                st.warning("No hay registros con motivo de retiro para Planta.")
        else:
            st.warning("No hay datos de motivos de retiro disponibles para Planta.")
    
    # Pestaña 3: Análisis Manipuladoras
    with tab3:
        st.markdown("### Análisis de Motivos de Retiro - Manipuladoras")
        
        if 'motivo_retiro' in manipuladoras_df.columns and not manipuladoras_df.empty:
            # Filtrar registros con motivo de retiro (no nulos)
            manipuladoras_con_motivo = manipuladoras_df.dropna(subset=['motivo_retiro'])
            
            if not manipuladoras_con_motivo.empty:
                # Análisis de motivos
                motivos_manipuladoras = manipuladoras_con_motivo['motivo_retiro'].value_counts().reset_index()
                motivos_manipuladoras.columns = ['motivo', 'conteo']
                
                # Mostrar métricas
                total_retiros = motivos_manipuladoras['conteo'].sum()
                st.metric("Total de registros con motivo de retiro", f"{total_retiros}")
                
                # Gráfico de barras
                fig_manipuladoras = px.bar(
                    motivos_manipuladoras.head(15),  # Top 15 motivos
                    x='motivo',
                    y='conteo',
                    title='Principales Motivos de Retiro - Manipuladoras',
                    labels={'motivo': 'Motivo', 'conteo': 'Cantidad'},
                    color='conteo',
                    color_continuous_scale='Reds'
                )
                
                st.plotly_chart(fig_manipuladoras, use_container_width=True)
                
                # Análisis por programa si está disponible
                if 'programa' in manipuladoras_con_motivo.columns:
                    st.markdown("#### Motivos de Retiro por Programa")
                    
                    # Agrupar por programa y motivo
                    programa_motivo = manipuladoras_con_motivo.groupby(['programa', 'motivo_retiro']).size().reset_index(name='conteo')
                    
                    # Obtener los programas con más retiros
                    top_programas = manipuladoras_con_motivo['programa'].value_counts().nlargest(5).index.tolist()
                    
                    # Filtrar para los programas principales
                    programa_motivo_top = programa_motivo[programa_motivo['programa'].isin(top_programas)]
                    
                    # Crear gráfico
                    fig_programa_motivo = px.bar(
                        programa_motivo_top,
                        x='motivo_retiro',
                        y='conteo',
                        color='programa',
                        title='Motivos de Retiro por Programa Principal',
                        labels={'motivo_retiro': 'Motivo', 'conteo': 'Cantidad', 'programa': 'Programa'},
                        barmode='group'
                    )
                    
                    # Ajustar layout
                    fig_programa_motivo.update_layout(
                        xaxis={'categoryorder':'total descending'},
                        height=500
                    )
                    
                    st.plotly_chart(fig_programa_motivo, use_container_width=True)
                
                # Mostrar tabla completa de motivos
                st.subheader("Tabla Completa - Motivos de Retiro Manipuladoras")
                st.dataframe(motivos_manipuladoras)
            else:
                st.warning("No hay registros con motivo de retiro para Manipuladoras.")
        else:
            st.warning("No hay datos de motivos de retiro disponibles para Manipuladoras.")
    
    # Análisis combinado de Motivo de Retiro por Empresa/Programa - SOLO LA TABLA CRUZADA
    st.subheader("Tabla Cruzada: Motivos de Retiro por Entidad")
    
    # Preparar los datos: entidades de la tabla Planta (empresas) y Manipuladoras (programas)
    planta_data = None
    if 'motivo_retiro' in planta_df.columns and 'empresa' in planta_df.columns and not planta_df.empty:
        planta_con_motivo = planta_df.dropna(subset=['motivo_retiro', 'empresa'])
        if not planta_con_motivo.empty:
            planta_data = planta_con_motivo[['empresa', 'motivo_retiro']].copy()
            planta_data['tipo_entidad'] = 'Empresa'
            planta_data['fuente'] = 'Planta'
            planta_data.rename(columns={'empresa': 'entidad'}, inplace=True)
    
    manipuladoras_data = None
    if 'motivo_retiro' in manipuladoras_df.columns and 'programa' in manipuladoras_df.columns and not manipuladoras_df.empty:
        manipuladoras_con_motivo = manipuladoras_df.dropna(subset=['motivo_retiro', 'programa'])
        if not manipuladoras_con_motivo.empty:
            manipuladoras_data = manipuladoras_con_motivo[['programa', 'motivo_retiro']].copy()
            manipuladoras_data['tipo_entidad'] = 'Programa'
            manipuladoras_data['fuente'] = 'Manipuladoras'
            manipuladoras_data.rename(columns={'programa': 'entidad'}, inplace=True)
    
    # Combinar los datos si existen
    combined_data = pd.DataFrame()
    if planta_data is not None:
        combined_data = pd.concat([combined_data, planta_data])
    if manipuladoras_data is not None:
        combined_data = pd.concat([combined_data, manipuladoras_data])
    
    if not combined_data.empty:
        try:
            # Agrupar por entidad, tipo_entidad, fuente y motivo
            cross_data = combined_data.groupby(['entidad', 'tipo_entidad', 'fuente', 'motivo_retiro']).size().reset_index(name='conteo')
            
            # Crear matriz de cruce para los principales motivos y entidades
            top_10_motivos = cross_data.groupby('motivo_retiro')['conteo'].sum().nlargest(10).index.tolist()
            top_15_entidades = cross_data.groupby('entidad')['conteo'].sum().nlargest(15).index.tolist()
            
            # Filtrar para los motivos y entidades principales
            top_filtered_data = cross_data[
                cross_data['motivo_retiro'].isin(top_10_motivos) & 
                cross_data['entidad'].isin(top_15_entidades)
            ]
            
            # Agrupar por entidad y motivo para una vista más clara
            summary_data = top_filtered_data.groupby(['entidad', 'tipo_entidad', 'motivo_retiro'])['conteo'].sum().reset_index()
            
            # Crear tabla pivot para mejor visualización
            pivot_table = pd.pivot_table(
                summary_data,
                values='conteo',
                index=['entidad', 'tipo_entidad'],
                columns='motivo_retiro',
                fill_value=0
            ).reset_index()
            
            # Mostrar la tabla cruzada
            st.dataframe(pivot_table)
            
        except Exception as e:
            st.error(f"Error al procesar los datos combinados: {e}")
            st.warning("Mostrando tabla simplificada")
            
            if not combined_data.empty:
                aggregated_data = combined_data.groupby(['entidad', 'tipo_entidad', 'motivo_retiro']).size().reset_index(name='conteo')
                st.dataframe(aggregated_data)
    else:
        st.warning("No hay suficientes datos para la tabla cruzada de motivos de retiro.")