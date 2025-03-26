import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import load_all_data

def run():
    """
    Módulo que muestra la tabla con el conteo total de tipos de contrato,
    combinando datos de las tablas Manipuladoras y Planta, con filtros en la barra lateral.
    """
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras'].copy()
        planta_df = data_dict['planta'].copy()
    
    # ---------- FILTROS EN LA BARRA LATERAL ----------
    st.sidebar.header("Filtros")
    
    # 1. FILTRO DE TIPO DE NOVEDAD (MULTISELECT)
    # Obtener valores únicos de tipo de novedad de ambas tablas
    tipos_novedad_manipuladoras = []
    tipos_novedad_planta = []
    
    # Verificar columnas en manipuladoras
    if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in manipuladoras_df.columns:
        manipuladoras_df['tipo_novedad'] = manipuladoras_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        tipos_novedad_manipuladoras = manipuladoras_df['tipo_novedad'].dropna().unique().tolist()
    
    # Verificar columnas en planta
    if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in planta_df.columns:
        planta_df['tipo_novedad'] = planta_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        tipos_novedad_planta = planta_df['tipo_novedad'].dropna().unique().tolist()
    
    # Combinar y eliminar duplicados
    todos_tipos_novedad = sorted(list(set(tipos_novedad_manipuladoras + tipos_novedad_planta)))
    
    if not todos_tipos_novedad:
        st.sidebar.warning("No se encontraron tipos de novedad en los datos.")
        todos_tipos_novedad = ["ACTIVO", "RETIRADO", "CASO ESPECIAL"]  # Valores por defecto
    
    # Multiselect para seleccionar múltiples opciones
    tipos_novedad_seleccionados = st.sidebar.multiselect(
        "Tipo de Novedad",
        options=todos_tipos_novedad,
        default=todos_tipos_novedad
    )
    
    # Si no hay selección, mostrar advertencia
    if not tipos_novedad_seleccionados:
        st.sidebar.warning("Por favor, seleccione al menos un tipo de novedad.")
        tipos_novedad_seleccionados = todos_tipos_novedad  # Usar todos como respaldo
    
    # 2. FILTRO DE FECHAS
    st.sidebar.subheader("Rango de Fechas")
    
    # Determinar qué columnas de fechas usar según el filtro de novedad
    columnas_fecha = []
    
    # Preparar las fechas en los DataFrames para el filtrado
    # Fechas de ingreso para manipuladoras
    if 'FECHA DE INGRESO (AAAAMMDD)' in manipuladoras_df.columns:
        manipuladoras_df['fecha_ingreso'] = pd.to_datetime(
            manipuladoras_df['FECHA DE INGRESO (AAAAMMDD)'], 
            format='%Y%m%d', 
            errors='coerce'
        )
    
    # Fechas de retiro para manipuladoras
    if 'FECHA DE RETIRO (AAAAMMDD)' in manipuladoras_df.columns:
        manipuladoras_df['fecha_retiro'] = pd.to_datetime(
            manipuladoras_df['FECHA DE RETIRO (AAAAMMDD)'], 
            format='%Y%m%d', 
            errors='coerce'
        )
    
    # Fechas de ingreso para planta
    if 'FECHA DE INGRESO (AAAAMMDD)' in planta_df.columns:
        planta_df['fecha_ingreso'] = pd.to_datetime(
            planta_df['FECHA DE INGRESO (AAAAMMDD)'], 
            format='%Y%m%d', 
            errors='coerce'
        )
    
    # Fechas de retiro para planta
    if 'FECHA DE RETIRO (AAAAMMDD)' in planta_df.columns:
        planta_df['fecha_retiro'] = pd.to_datetime(
            planta_df['FECHA DE RETIRO (AAAAMMDD)'], 
            format='%Y%m%d', 
            errors='coerce'
        )
    
    # Obtener todas las fechas según el tipo de novedad seleccionado
    fechas = []
    
    # Determinar qué columnas de fecha usar según el filtro de novedad
    if any(item in ["ACTIVO", "CASO ESPECIAL"] for item in tipos_novedad_seleccionados):
        st.sidebar.text("Se usarán Fechas de Ingreso para ACTIVO/CASO ESPECIAL")
        if 'fecha_ingreso' in manipuladoras_df.columns:
            fechas.extend(manipuladoras_df['fecha_ingreso'].dropna().tolist())
        if 'fecha_ingreso' in planta_df.columns:
            fechas.extend(planta_df['fecha_ingreso'].dropna().tolist())
    
    if "RETIRADO" in tipos_novedad_seleccionados:
        st.sidebar.text("Se usarán Fechas de Retiro para RETIRADO")
        if 'fecha_retiro' in manipuladoras_df.columns:
            fechas.extend(manipuladoras_df['fecha_retiro'].dropna().tolist())
        if 'fecha_retiro' in planta_df.columns:
            fechas.extend(planta_df['fecha_retiro'].dropna().tolist())
    
    # Determinar el rango de fechas disponible
    if fechas:
        min_date = min(filter(lambda x: not pd.isna(x), fechas))
        max_date = max(filter(lambda x: not pd.isna(x), fechas))
    else:
        # Fechas por defecto si no hay datos
        min_date = datetime.now() - timedelta(days=365)
        max_date = datetime.now()
    
    # Selector de rango de fechas
    date_range = st.sidebar.date_input(
        "Seleccione rango de fechas",
        value=(min_date.date() if hasattr(min_date, 'date') else min_date,
               max_date.date() if hasattr(max_date, 'date') else max_date),
        key="date_range"
    )
    
    # Asegurarse de que date_range sea una tupla
    if isinstance(date_range, datetime) or not hasattr(date_range, '__len__'):
        date_range = (date_range, date_range)
    elif len(date_range) == 1:
        date_range = (date_range[0], date_range[0])
    
    # Convertir a timestamps de pandas para el filtrado
    fecha_min = pd.Timestamp(date_range[0])
    fecha_max = pd.Timestamp(date_range[1])
    
    # ---------- APLICAR FILTROS A LOS DATOS ----------
    manipuladoras_filtradas = manipuladoras_df.copy()
    planta_filtrada = planta_df.copy()
    
    # 1. Filtrar por tipo de novedad
    if 'tipo_novedad' in manipuladoras_filtradas.columns:
        manipuladoras_filtradas = manipuladoras_filtradas[
            manipuladoras_filtradas['tipo_novedad'].isin(tipos_novedad_seleccionados)
        ]
    
    if 'tipo_novedad' in planta_filtrada.columns:
        planta_filtrada = planta_filtrada[
            planta_filtrada['tipo_novedad'].isin(tipos_novedad_seleccionados)
        ]
    
    # 2. Filtrar por fechas
    # Crear máscaras para cada DataFrame
    manipuladoras_mask = pd.Series(False, index=manipuladoras_filtradas.index)
    planta_mask = pd.Series(False, index=planta_filtrada.index)
    
    # Aplicar filtros según tipo de novedad
    if any(item in ["ACTIVO", "CASO ESPECIAL"] for item in tipos_novedad_seleccionados):
        # Filtrar manipuladoras por fecha de ingreso
        if 'fecha_ingreso' in manipuladoras_filtradas.columns:
            mask_ingreso = (
                (manipuladoras_filtradas['fecha_ingreso'] >= fecha_min) & 
                (manipuladoras_filtradas['fecha_ingreso'] <= fecha_max) &
                (manipuladoras_filtradas['tipo_novedad'].isin(['ACTIVO', 'CASO ESPECIAL']))
            )
            manipuladoras_mask = manipuladoras_mask | mask_ingreso
        
        # Filtrar planta por fecha de ingreso
        if 'fecha_ingreso' in planta_filtrada.columns:
            mask_ingreso = (
                (planta_filtrada['fecha_ingreso'] >= fecha_min) & 
                (planta_filtrada['fecha_ingreso'] <= fecha_max) &
                (planta_filtrada['tipo_novedad'].isin(['ACTIVO', 'CASO ESPECIAL']))
            )
            planta_mask = planta_mask | mask_ingreso
    
    if "RETIRADO" in tipos_novedad_seleccionados:
        # Filtrar manipuladoras por fecha de retiro
        if 'fecha_retiro' in manipuladoras_filtradas.columns:
            mask_retiro = (
                (manipuladoras_filtradas['fecha_retiro'] >= fecha_min) & 
                (manipuladoras_filtradas['fecha_retiro'] <= fecha_max) &
                (manipuladoras_filtradas['tipo_novedad'] == 'RETIRADO')
            )
            manipuladoras_mask = manipuladoras_mask | mask_retiro
        
        # Filtrar planta por fecha de retiro
        if 'fecha_retiro' in planta_filtrada.columns:
            mask_retiro = (
                (planta_filtrada['fecha_retiro'] >= fecha_min) & 
                (planta_filtrada['fecha_retiro'] <= fecha_max) &
                (planta_filtrada['tipo_novedad'] == 'RETIRADO')
            )
            planta_mask = planta_mask | mask_retiro
    
    # Aplicar las máscaras
    manipuladoras_filtradas = manipuladoras_filtradas[manipuladoras_mask]
    planta_filtrada = planta_filtrada[planta_mask]
    
    # ---------- MOSTRAR INFORMACIÓN DE RESULTADOS ----------
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Registros filtrados en Manipuladoras: {len(manipuladoras_filtradas)}")
    with col2:
        st.info(f"Registros filtrados en Planta: {len(planta_filtrada)}")
    
    # ---------- PROCESAMIENTO PARA LA TABLA DE RESULTADOS ----------
    # Verificar que existan las columnas de tipo de contrato
    if 'tipo_contrato' not in manipuladoras_filtradas.columns:
        if 'TIPO DE CONTRATO' in manipuladoras_filtradas.columns:
            manipuladoras_filtradas['tipo_contrato'] = manipuladoras_filtradas['TIPO DE CONTRATO']
        else:
            st.error("No se encontró la columna de tipo de contrato en la tabla Manipuladoras")
            return
        
    if 'tipo_contrato' not in planta_filtrada.columns:
        if 'TIPO DE CONTRATO' in planta_filtrada.columns:
            planta_filtrada['tipo_contrato'] = planta_filtrada['TIPO DE CONTRATO']
        else:
            st.error("No se encontró la columna de tipo de contrato en la tabla Planta")
            return
    
    # Combinar los tipos de contrato de ambas fuentes
    tipos_contrato_manipuladoras = manipuladoras_filtradas['tipo_contrato'].dropna()
    tipos_contrato_planta = planta_filtrada['tipo_contrato'].dropna()
    
    # Concatenar las series
    todos_tipos_contrato = pd.concat([tipos_contrato_manipuladoras, tipos_contrato_planta])
    
    # Contar los valores y ordenar por frecuencia descendente
    conteo_tipos = todos_tipos_contrato.value_counts().reset_index()
    conteo_tipos.columns = ['Tipo de Contrato', 'Total']
    
    # Mostrar la tabla con los conteos
    st.header("Conteo Total de Tipos de Contrato")
    
    # Verificar si hay datos para mostrar
    if len(conteo_tipos) > 0:
        st.dataframe(conteo_tipos, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados.")