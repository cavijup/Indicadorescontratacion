import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data, filter_by_date_range, filter_by_novedad, get_all_novedades_types

def run():
    """
    Muestra el análisis y visualización de empresas, programas y áreas
    de las tres hojas del libro de Google Sheets.
    """
    st.title("Análisis de Empresas, Programas y Áreas")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']
        aprendices_df = data_dict['aprendices']

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
        
        if not aprendices_df.empty and 'tipo_novedad' in aprendices_df.columns:
            aprendices_df = filter_by_novedad(aprendices_df, selected_novedades)
        
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
        
        if not aprendices_df.empty and 'tipo_novedad' in aprendices_df.columns:
            aprendices_df = filter_by_novedad(aprendices_df, st.session_state.selected_novedades)
    
    # Botón para limpiar filtro de novedad
    if st.session_state.get('novedad_filtro_aplicado', False):
        if st.sidebar.button("Limpiar filtro de novedad"):
            # Volver a cargar los datos originales
            data_dict = load_all_data()
            manipuladoras_df = data_dict['manipuladoras']
            planta_df = data_dict['planta']
            aprendices_df = data_dict['aprendices']
            
            # Limpiar estado del filtro
            st.session_state.novedad_filtro_aplicado = False
            if 'selected_novedades' in st.session_state:
                del st.session_state.selected_novedades
            
            st.sidebar.success("Filtro de novedad eliminado. Mostrando todos los tipos de novedad.")
            st.experimental_rerun()  # Volver a ejecutar la app para actualizar la interfaz

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
        
        # Botón para aplicar filtro de fechas
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
            
            st.sidebar.success(f"Filtro de fechas aplicado: {start_date} a {end_date}")
        # Mostrar estado del filtro actual
        elif st.session_state.get('filtro_aplicado', False):
            st.sidebar.info(f"Filtro de fechas actual: {st.session_state.start_date} a {st.session_state.end_date}")
            
            # Si hay filtro guardado en la sesión, aplicarlo
            if not manipuladoras_df.empty and 'fecha_ingreso' in manipuladoras_df.columns:
                manipuladoras_df = filter_by_date_range(manipuladoras_df, 
                                                       pd.Timestamp(st.session_state.start_date), 
                                                       pd.Timestamp(st.session_state.end_date))
            
            if not planta_df.empty and 'fecha_ingreso' in planta_df.columns:
                planta_df = filter_by_date_range(planta_df, 
                                               pd.Timestamp(st.session_state.start_date), 
                                               pd.Timestamp(st.session_state.end_date))
            
            if not aprendices_df.empty and 'fecha_ingreso' in aprendices_df.columns:
                aprendices_df = filter_by_date_range(aprendices_df, 
                                                   pd.Timestamp(st.session_state.start_date), 
                                                   pd.Timestamp(st.session_state.end_date))
        
        # Botón para limpiar filtro de fechas
        if st.session_state.get('filtro_aplicado', False):
            if st.sidebar.button("Limpiar filtro de fechas"):
                # Volver a cargar los datos originales (pero mantener el filtro de novedad si está activo)
                data_dict = load_all_data()
                manipuladoras_df = data_dict['manipuladoras']
                planta_df = data_dict['planta']
                aprendices_df = data_dict['aprendices']
                
                # Aplicar el filtro de novedad si está activo
                if st.session_state.get('novedad_filtro_aplicado', False):
                    if not manipuladoras_df.empty and 'tipo_novedad' in manipuladoras_df.columns:
                        manipuladoras_df = filter_by_novedad(manipuladoras_df, st.session_state.selected_novedades)
                    
                    if not planta_df.empty and 'tipo_novedad' in planta_df.columns:
                        planta_df = filter_by_novedad(planta_df, st.session_state.selected_novedades)
                    
                    if not aprendices_df.empty and 'tipo_novedad' in aprendices_df.columns:
                        aprendices_df = filter_by_novedad(aprendices_df, st.session_state.selected_novedades)
                
                # Limpiar estado del filtro de fechas
                st.session_state.filtro_aplicado = False
                if 'start_date' in st.session_state:
                    del st.session_state.start_date
                if 'end_date' in st.session_state:
                    del st.session_state.end_date
                
                st.sidebar.success("Filtro de fechas eliminado.")
                st.experimental_rerun()  # Volver a ejecutar la app para actualizar la interfaz
    
    # El resto del código del módulo Empresas.py permanece sin cambios
    # Análisis de distribución por empresa/programa/área
    st.subheader("Distribución por Empresa, Programa y Área")
       
    # Análisis de distribución por empresa/programa/área
    st.subheader("Distribución por Empresa, Programa y Área")
    
    # Preparar datos para cada tipo
    empresas_data = []
    
    # Programas para Manipuladoras
    if 'programa' in manipuladoras_df.columns and not manipuladoras_df.empty:
        programas = manipuladoras_df['programa'].value_counts().reset_index()
        programas.columns = ['entidad', 'conteo']
        programas['tipo'] = 'Programa'
        programas['fuente'] = 'Manipuladoras'
        empresas_data.append(programas)
    
    # Empresas para Planta
    if 'empresa' in planta_df.columns and not planta_df.empty:
        empresas = planta_df['empresa'].value_counts().reset_index()
        empresas.columns = ['entidad', 'conteo']
        empresas['tipo'] = 'Empresa'
        empresas['fuente'] = 'Planta'
        empresas_data.append(empresas)
    
    # Áreas para Aprendices
    if 'area' in aprendices_df.columns and not aprendices_df.empty:
        areas = aprendices_df['area'].value_counts().reset_index()
        areas.columns = ['entidad', 'conteo']
        areas['tipo'] = 'Área'
        areas['fuente'] = 'Aprendices'
        empresas_data.append(areas)
    
    if empresas_data:
        # Combinar todos los datos
        combined_data = pd.concat(empresas_data, ignore_index=True)
        
        # Crear gráfico de barras horizontal
        fig = px.bar(
            combined_data,
            y='entidad',
            x='conteo',
            color='fuente',
            facet_col='tipo',
            title='Distribución por Empresa, Programa y Área',
            labels={'entidad': 'Entidad', 'conteo': 'Cantidad', 'fuente': 'Fuente', 'tipo': 'Tipo'},
            height=max(400, len(combined_data) * 20)  # Ajustar altura según cantidad de datos
        )
        
        # Actualizar layout para mejor visualización
        fig.update_layout(xaxis_title='Cantidad')
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla de datos
        st.subheader("Tabla de Datos - Empresas, Programas y Áreas")
        st.dataframe(combined_data)
    else:
        st.warning("No hay datos suficientes para analizar empresas, programas o áreas.")
    
    # Análisis detallado por fuente
    st.subheader("Análisis Detallado por Fuente")
    
    tab1, tab2, tab3 = st.tabs(["Manipuladoras (Programas)", "Planta (Empresas)", "Aprendices (Áreas)"])
    
    with tab1:
        if 'programa' in manipuladoras_df.columns and not manipuladoras_df.empty:
            st.markdown("### Programas - Manipuladoras")
            
            # Top 10 programas
            top_programas = manipuladoras_df['programa'].value_counts().nlargest(10).reset_index()
            top_programas.columns = ['programa', 'conteo']
            
            # Crear gráfico de barras
            fig_programas = px.bar(
                top_programas,
                x='programa',
                y='conteo',
                title='Top 10 Programas - Manipuladoras',
                labels={'programa': 'Programa', 'conteo': 'Cantidad'},
                color='conteo',
                color_continuous_scale='Blues'
            )
            
            st.plotly_chart(fig_programas, use_container_width=True)
            
            # Análisis cruzado: Programas por Tipo de Contrato
            if 'tipo_contrato' in manipuladoras_df.columns:
                st.markdown("#### Distribución de Programas por Tipo de Contrato")
                
                # Agrupar por programa y tipo de contrato
                prog_contrato = manipuladoras_df.groupby(['programa', 'tipo_contrato']).size().reset_index(name='conteo')
                
                # Filtrar solo los programas más frecuentes para evitar gráfico sobrecargado
                top_programas_list = top_programas['programa'].tolist()
                prog_contrato_filtered = prog_contrato[prog_contrato['programa'].isin(top_programas_list)]
                
                # Crear gráfico de barras apiladas
                fig_prog_contrato = px.bar(
                    prog_contrato_filtered,
                    x='programa',
                    y='conteo',
                    color='tipo_contrato',
                    title='Distribución de Programas por Tipo de Contrato',
                    labels={'programa': 'Programa', 'conteo': 'Cantidad', 'tipo_contrato': 'Tipo de Contrato'}
                )
                
                st.plotly_chart(fig_prog_contrato, use_container_width=True)
        else:
            st.warning("No hay datos de programas disponibles para Manipuladoras")
    
    with tab2:
        if 'empresa' in planta_df.columns and not planta_df.empty:
            st.markdown("### Empresas - Planta")
            
            # Top 10 empresas
            top_empresas = planta_df['empresa'].value_counts().nlargest(10).reset_index()
            top_empresas.columns = ['empresa', 'conteo']
            
            # Crear gráfico de barras
            fig_empresas = px.bar(
                top_empresas,
                x='empresa',
                y='conteo',
                title='Top 10 Empresas - Planta',
                labels={'empresa': 'Empresa', 'conteo': 'Cantidad'},
                color='conteo',
                color_continuous_scale='Greens'
            )
            
            st.plotly_chart(fig_empresas, use_container_width=True)
            
            # Análisis cruzado: Empresas por Tipo de Contrato
            if 'tipo_contrato' in planta_df.columns:
                st.markdown("#### Distribución de Empresas por Tipo de Contrato")
                
                # Agrupar por empresa y tipo de contrato
                emp_contrato = planta_df.groupby(['empresa', 'tipo_contrato']).size().reset_index(name='conteo')
                
                # Filtrar solo las empresas más frecuentes para evitar gráfico sobrecargado
                top_empresas_list = top_empresas['empresa'].tolist()
                emp_contrato_filtered = emp_contrato[emp_contrato['empresa'].isin(top_empresas_list)]
                
                # Crear gráfico de barras apiladas
                fig_emp_contrato = px.bar(
                    emp_contrato_filtered,
                    x='empresa',
                    y='conteo',
                    color='tipo_contrato',
                    title='Distribución de Empresas por Tipo de Contrato',
                    labels={'empresa': 'Empresa', 'conteo': 'Cantidad', 'tipo_contrato': 'Tipo de Contrato'}
                )
                
                st.plotly_chart(fig_emp_contrato, use_container_width=True)
        else:
            st.warning("No hay datos de empresas disponibles para Planta")
    
    with tab3:
        if 'area' in aprendices_df.columns and not aprendices_df.empty:
            st.markdown("### Áreas - Aprendices")
            
            # Top 10 áreas
            top_areas = aprendices_df['area'].value_counts().nlargest(10).reset_index()
            top_areas.columns = ['area', 'conteo']
            
            # Crear gráfico de barras
            fig_areas = px.bar(
                top_areas,
                x='area',
                y='conteo',
                title='Top 10 Áreas - Aprendices',
                labels={'area': 'Área', 'conteo': 'Cantidad'},
                color='conteo',
                color_continuous_scale='Reds'
            )
            
            st.plotly_chart(fig_areas, use_container_width=True)
            
            # Análisis cruzado: Áreas por Tipo de Contrato
            if 'tipo_contrato' in aprendices_df.columns:
                st.markdown("#### Distribución de Áreas por Tipo de Contrato")
                
                # Agrupar por área y tipo de contrato
                area_contrato = aprendices_df.groupby(['area', 'tipo_contrato']).size().reset_index(name='conteo')
                
                # Filtrar solo las áreas más frecuentes para evitar gráfico sobrecargado
                top_areas_list = top_areas['area'].tolist()
                area_contrato_filtered = area_contrato[area_contrato['area'].isin(top_areas_list)]
                
                # Crear gráfico de barras apiladas
                fig_area_contrato = px.bar(
                    area_contrato_filtered,
                    x='area',
                    y='conteo',
                    color='tipo_contrato',
                    title='Distribución de Áreas por Tipo de Contrato',
                    labels={'area': 'Área', 'conteo': 'Cantidad', 'tipo_contrato': 'Tipo de Contrato'}
                )
                
                st.plotly_chart(fig_area_contrato, use_container_width=True)
        else:
            st.warning("No hay datos de áreas disponibles para Aprendices")