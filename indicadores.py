import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import (
    load_all_data, 
    get_unique_tipos_novedad,
    filter_data_by_novedad,
    get_date_range_by_novedad,
    filter_data_by_date_range
)

def render_sidebar_filters():
    """
    Renderiza los filtros en la barra lateral y retorna los datos filtrados.
    """
    st.sidebar.header("Filtros")
    
    # Cargar datos
    with st.spinner("Cargando datos para filtros..."):
        data_dict = load_all_data()
        
        # 1. Filtro de Tipo de Novedad
        tipos_novedad = get_unique_tipos_novedad()
        
        if not tipos_novedad:
            st.sidebar.warning("No se encontraron tipos de novedad en los datos.")
            return data_dict
        
        # Seleccionar todos por defecto
        tipos_novedad_seleccionados = st.sidebar.multiselect(
            "Tipo de Novedad",
            options=tipos_novedad,
            default=tipos_novedad
        )
        
        if not tipos_novedad_seleccionados:
            st.sidebar.warning("Por favor, seleccione al menos un tipo de novedad.")
            return data_dict
        
        # Filtrar datos por tipo de novedad
        filtered_data = filter_data_by_novedad(data_dict, tipos_novedad_seleccionados)
        
        # 2. Filtro de Fecha (dependiente del primer filtro)
        st.sidebar.subheader("Rango de Fechas")
        
        # Obtener rango de fechas disponible según el tipo de novedad
        min_date, max_date = get_date_range_by_novedad(filtered_data, tipos_novedad_seleccionados)
        
        # Determinar etiqueta de fecha según selección
        if set(tipos_novedad_seleccionados).issubset({'ACTIVO', 'CASO ESPECIAL'}):
            fecha_label = "Fechas de Ingreso"
        elif 'RETIRADO' in tipos_novedad_seleccionados and not any(x in tipos_novedad_seleccionados for x in ['ACTIVO', 'CASO ESPECIAL']):
            fecha_label = "Fechas de Retiro"
        else:
            fecha_label = "Fechas de Ingreso/Retiro"
        
        st.sidebar.text(fecha_label)
        
        # Convertir a datetime si es necesario
        if not isinstance(min_date, datetime):
            try:
                min_date = datetime.strptime(str(min_date), '%Y-%m-%d')
            except:
                min_date = datetime.now() - timedelta(days=365)
        
        if not isinstance(max_date, datetime):
            try:
                max_date = datetime.strptime(str(max_date), '%Y-%m-%d')
            except:
                max_date = datetime.now()
        
        # Selector de rango de fechas
        date_range = st.sidebar.date_input(
            "Seleccione rango de fechas",
            value=(min_date, max_date),
            min_value=min_date - timedelta(days=365*5),  # Permitir fechas hasta 5 años antes
            max_value=datetime.now() + timedelta(days=30)  # Permitir fechas hasta 1 mes en el futuro
        )
        
        # Convertir a tupla si es una fecha única
        if isinstance(date_range, datetime):
            date_range = (date_range, date_range)
        
        # Si el usuario seleccionó un rango válido
        if len(date_range) == 2:
            # Convertir a timestamps de pandas para comparación
            date_min = pd.Timestamp(date_range[0])
            date_max = pd.Timestamp(date_range[1])
            
            # Filtrar por rango de fechas
            filtered_data = filter_data_by_date_range(filtered_data, tipos_novedad_seleccionados, (date_min, date_max))
        
        # Botón para limpiar filtros
        if st.sidebar.button("Limpiar Filtros"):
            st.experimental_rerun()
        
        return filtered_data

def run():
    """
    Módulo que muestra la tabla con el conteo total de tipos de contrato,
    combinando datos de las tablas Manipuladoras y Planta, con filtros en la barra lateral.
    """
    # Renderizar filtros en la barra lateral y obtener datos filtrados
    filtered_data = render_sidebar_filters()
    
    # Extraer los DataFrames filtrados
    manipuladoras_df = filtered_data['manipuladoras']
    planta_df = filtered_data['planta']
    
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
    
    # Mostrar información sobre los datos filtrados
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Registros en Manipuladoras: {len(manipuladoras_df)}")
    with col2:
        st.info(f"Registros en Planta: {len(planta_df)}")
    
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
    
    # Verificar si hay datos para mostrar
    if len(conteo_tipos) > 0:
        st.dataframe(conteo_tipos, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados.")