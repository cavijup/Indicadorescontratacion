import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_all_data, filter_by_date_range, filter_by_novedad, get_all_novedades_types

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

    # Añadir filtro por rango de fechas (existente)
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
                
    # Añadir botón para incluir retirados del mes anterior
    st.sidebar.header("Opciones adicionales de análisis")

    incluir_retirados_mes_anterior = st.sidebar.button("✅ Incluir retirados del mes anterior")

    if incluir_retirados_mes_anterior:
        # Guardar el estado en la sesión
        st.session_state.incluir_retirados_mes_anterior = True
        
        # Obtener el mes anterior
        today = pd.Timestamp.now()
        first_day_current_month = pd.Timestamp(today.year, today.month, 1)
        last_day_previous_month = first_day_current_month - pd.Timedelta(days=1)
        first_day_previous_month = pd.Timestamp(last_day_previous_month.year, last_day_previous_month.month, 1)
        
        # Guardar fechas del mes anterior en la sesión
        st.session_state.mes_anterior_inicio = first_day_previous_month
        st.session_state.mes_anterior_fin = last_day_previous_month
        
        st.sidebar.success(f"Se incluirán retirados del periodo: {first_day_previous_month.strftime('%d/%m/%Y')} - {last_day_previous_month.strftime('%d/%m/%Y')}")
        
    elif st.session_state.get('incluir_retirados_mes_anterior', False):
        # Mostrar mensaje si el filtro ya está activo
        inicio = st.session_state.mes_anterior_inicio
        fin = st.session_state.mes_anterior_fin
        st.sidebar.info(f"Incluyendo retirados del periodo: {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}")
        
    # Botón para desactivar la inclusión de retirados del mes anterior
    if st.session_state.get('incluir_retirados_mes_anterior', False):
        if st.sidebar.button("❌ Quitar retirados del mes anterior"):
            st.session_state.incluir_retirados_mes_anterior = False
            if 'mes_anterior_inicio' in st.session_state:
                del st.session_state.mes_anterior_inicio
            if 'mes_anterior_fin' in st.session_state:
                del st.session_state.mes_anterior_fin
            st.sidebar.success("Se han eliminado los retirados del mes anterior del análisis.")
            st.experimental_rerun()
    
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