import streamlit as st
import pandas as pd
from utils import load_all_data, filter_by_date_range, filter_by_novedad, get_all_novedades_types

def run():
    """
    Módulo que muestra únicamente una tabla con el conteo total de tipos de contrato,
    combinando datos de las tablas Manipuladoras y Planta, con filtros por fecha y tipo de novedad.
    """
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras']
        planta_df = data_dict['planta']

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
    st.sidebar.header("Filtrar por fecha de ingreso")

    # Determinar las fechas mínima y máxima entre todos los DataFrames
    min_dates = []
    max_dates = []

    for df_name, df in [("Manipuladoras", manipuladoras_df), ("Planta", planta_df)]:
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
            
            # Guardar estado del filtro
            st.session_state.filtro_aplicado = True
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            
            st.sidebar.success(f"Filtro aplicado: {start_date} a {end_date}")
        # Mostrar estado del filtro actual
        elif st.session_state.get('filtro_aplicado', False):
            st.sidebar.info(f"Filtro actual: {st.session_state.start_date} a {st.session_state.end_date}")
            
            # Si hay filtro guardado en la sesión, aplicarlo
            if not manipuladoras_df.empty and 'fecha_ingreso' in manipuladoras_df.columns:
                manipuladoras_df = filter_by_date_range(manipuladoras_df, 
                                                       pd.Timestamp(st.session_state.start_date), 
                                                       pd.Timestamp(st.session_state.end_date))
            
            if not planta_df.empty and 'fecha_ingreso' in planta_df.columns:
                planta_df = filter_by_date_range(planta_df, 
                                               pd.Timestamp(st.session_state.start_date), 
                                               pd.Timestamp(st.session_state.end_date))
            
        # Botón para limpiar filtro
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
                
                # Limpiar estado del filtro
                st.session_state.filtro_aplicado = False
                if 'start_date' in st.session_state:
                    del st.session_state.start_date
                if 'end_date' in st.session_state:
                    del st.session_state.end_date
                
                st.sidebar.success("Filtro de fechas eliminado.")
                st.experimental_rerun()  # Volver a ejecutar la app para actualizar la interfaz

    # Verificar que existan las columnas de interés
    if 'tipo_contrato' not in manipuladoras_df.columns:
        if 'TIPO DE CONTRATO' in manipuladoras_df.columns:
            manipuladoras_df['tipo_contrato'] = manipuladoras_df['TIPO DE CONTRATO']
        else:
            st.error("No se encontró la columna de tipo de contrato en la tabla Manipuladoras")
            return
        
    if 'tipo_contrato' not in planta_df.columns:
        if 'TIPO DE CONTRATO' in planta_df.columns:
            planta_df['tipo_contrato'] = planta_df['TIPO DE CONTRATO']
        else:
            st.error("No se encontró la columna de tipo de contrato en la tabla Planta")
            return
    
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