import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import load_all_data

def run():
    """
    Módulo que muestra la agrupación de personal activo según:
    - PROGRAMA AL QUE PERTENECE (Manipuladoras, columna H)
    - AREA (Aprendices, columna F)
    - AREA (Planta, columna N)
    Además filtra específicamente registros de BUGA en la tabla Planta.
    """
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras'].copy()
        planta_df = data_dict['planta'].copy() 
        aprendices_df = data_dict['aprendices'].copy()
    
    # ---------- FILTROS EN LA BARRA LATERAL ----------
    st.sidebar.header("Filtros")
    
    # 1. FILTRO DE TIPO DE NOVEDAD (MULTISELECT)
    # Obtener valores únicos de tipo de novedad de todas las tablas
    tipos_novedad_manipuladoras = []
    tipos_novedad_planta = []
    tipos_novedad_aprendices = []
    
    # Verificar columnas en manipuladoras
    if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in manipuladoras_df.columns:
        manipuladoras_df['tipo_novedad'] = manipuladoras_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        tipos_novedad_manipuladoras = manipuladoras_df['tipo_novedad'].dropna().unique().tolist()
    
    # Verificar columnas en planta
    if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in planta_df.columns:
        planta_df['tipo_novedad'] = planta_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        tipos_novedad_planta = planta_df['tipo_novedad'].dropna().unique().tolist()
    
    # Verificar columnas en aprendices
    if 'TIPO DE NOVEDAD' in aprendices_df.columns:
        aprendices_df['tipo_novedad'] = aprendices_df['TIPO DE NOVEDAD']
        tipos_novedad_aprendices = aprendices_df['tipo_novedad'].dropna().unique().tolist()
    
    # Combinar y eliminar duplicados
    todos_tipos_novedad = sorted(list(set(tipos_novedad_manipuladoras + tipos_novedad_planta + tipos_novedad_aprendices)))
    
    if not todos_tipos_novedad:
        st.sidebar.warning("No se encontraron tipos de novedad en los datos.")
        todos_tipos_novedad = ["ACTIVO", "RETIRADO", "CASO ESPECIAL"]  # Valores por defecto
    
    # Multiselect para seleccionar múltiples opciones
    tipos_novedad_seleccionados = st.sidebar.multiselect(
        "Tipo de Novedad",
        options=todos_tipos_novedad,
        default=["ACTIVO"]  # Por defecto, mostrar solo activos
    )
    
    # Si no hay selección, mostrar advertencia
    if not tipos_novedad_seleccionados:
        st.sidebar.warning("Por favor, seleccione al menos un tipo de novedad.")
        tipos_novedad_seleccionados = ["ACTIVO"]  # Usar "ACTIVO" como respaldo
    
    # 2. FILTRO DE FECHAS (Igual que en las otras páginas)
    st.sidebar.subheader("Rango de Fechas")
    
    # Preparar las fechas en los DataFrames para el filtrado
    for df_name, df in [('manipuladoras', manipuladoras_df), ('planta', planta_df), ('aprendices', aprendices_df)]:
        # Fechas de ingreso
        if 'FECHA DE INGRESO (AAAAMMDD)' in df.columns:
            df['fecha_ingreso'] = pd.to_datetime(
                df['FECHA DE INGRESO (AAAAMMDD)'], 
                format='%Y%m%d', 
                errors='coerce'
            )
        
        # Fechas de retiro
        if 'FECHA DE RETIRO (AAAAMMDD)' in df.columns:
            df['fecha_retiro'] = pd.to_datetime(
                df['FECHA DE RETIRO (AAAAMMDD)'], 
                format='%Y%m%d', 
                errors='coerce'
            )
    
    # Obtener todas las fechas según el tipo de novedad seleccionado
    fechas = []
    
    # Determinar qué columnas de fecha usar según el filtro de novedad
    if any(item in ["ACTIVO", "CASO ESPECIAL"] for item in tipos_novedad_seleccionados):
        st.sidebar.text("Se usarán Fechas de Ingreso para ACTIVO/CASO ESPECIAL")
        for df in [manipuladoras_df, planta_df, aprendices_df]:
            if 'fecha_ingreso' in df.columns:
                fechas.extend(df['fecha_ingreso'].dropna().tolist())
    
    if "RETIRADO" in tipos_novedad_seleccionados:
        st.sidebar.text("Se usarán Fechas de Retiro para RETIRADO")
        for df in [manipuladoras_df, planta_df, aprendices_df]:
            if 'fecha_retiro' in df.columns:
                fechas.extend(df['fecha_retiro'].dropna().tolist())
    
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
        key="date_range_personal_activo"
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
    # Función para aplicar filtros a cada DataFrame
    def aplicar_filtros(df):
        # Crear una copia para no modificar el original
        df_filtrado = df.copy()
        
        # 1. Filtrar por tipo de novedad
        if 'tipo_novedad' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['tipo_novedad'].isin(tipos_novedad_seleccionados)
            ]
        
        # 2. Filtrar por fechas
        mask = pd.Series(False, index=df_filtrado.index)
        
        # Aplicar filtros según tipo de novedad
        if any(item in ["ACTIVO", "CASO ESPECIAL"] for item in tipos_novedad_seleccionados):
            if 'fecha_ingreso' in df_filtrado.columns:
                mask_ingreso = (
                    (df_filtrado['fecha_ingreso'] >= fecha_min) & 
                    (df_filtrado['fecha_ingreso'] <= fecha_max) &
                    (df_filtrado['tipo_novedad'].isin(['ACTIVO', 'CASO ESPECIAL']))
                )
                mask = mask | mask_ingreso
        
        if "RETIRADO" in tipos_novedad_seleccionados:
            if 'fecha_retiro' in df_filtrado.columns:
                mask_retiro = (
                    (df_filtrado['fecha_retiro'] >= fecha_min) & 
                    (df_filtrado['fecha_retiro'] <= fecha_max) &
                    (df_filtrado['tipo_novedad'] == 'RETIRADO')
                )
                mask = mask | mask_retiro
        
        # Aplicar la máscara
        df_filtrado = df_filtrado[mask]
        
        return df_filtrado
    
    # Aplicar filtros a cada DataFrame
    manipuladoras_filtradas = aplicar_filtros(manipuladoras_df)
    planta_filtrada = aplicar_filtros(planta_df)
    aprendices_filtrados = aplicar_filtros(aprendices_df)
    
    # ---------- MOSTRAR INFORMACIÓN DE RESULTADOS ----------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"Registros filtrados en Manipuladoras: {len(manipuladoras_filtradas)}")
    with col2:
        st.info(f"Registros filtrados en Planta: {len(planta_filtrada)}")
    with col3:
        st.info(f"Registros filtrados en Aprendices: {len(aprendices_filtrados)}")

    # ---------- BUSCAR COLUMNAS NECESARIAS ----------
    def encontrar_columna_por_posicion(df, posicion, nombre_alternativo=None):
        """Busca una columna por posición o nombre alternativo."""
        columna = None
        
        # 1. Buscar por posición
        if len(df.columns) > posicion:
            columna = df.columns[posicion]
        
        # 2. Si no se encuentra por posición, buscar por nombre alternativo
        if columna is None and nombre_alternativo:
            for nombre in nombre_alternativo:
                if nombre in df.columns:
                    columna = nombre
                    break
        
        return columna
    
    # Buscar las columnas necesarias
    manipuladoras_programa_col = encontrar_columna_por_posicion(
        manipuladoras_filtradas, 
        7,  # Posición H
        ['PROGRAMA AL QUE PERTENECE', 'Programa al que Pertenece', 'PROGRAMA']
    )
    
    aprendices_area_col = encontrar_columna_por_posicion(
        aprendices_filtrados, 
        5,  # Posición F
        ['AREA', 'ÁREA', 'Area', 'Área']
    )
    
    planta_area_col = encontrar_columna_por_posicion(
        planta_filtrada, 
        13,  # Posición N
        ['AREA', 'ÁREA', 'Area', 'Área']
    )
    
    # Mostrar advertencia si no se encuentran las columnas
    missing_cols = []
    if not manipuladoras_programa_col:
        missing_cols.append("PROGRAMA AL QUE PERTENECE (Manipuladoras, posición H)")
    if not aprendices_area_col:
        missing_cols.append("AREA (Aprendices, posición F)")
    if not planta_area_col:
        missing_cols.append("AREA (Planta, posición N)")
    
    if missing_cols:
        st.warning(f"No se encontraron las siguientes columnas: {', '.join(missing_cols)}")
        st.info("Por favor, verifica los nombres o posiciones de las columnas en los datos.")
    
    # ---------- CREAR TABLAS DE AGRUPACIÓN ----------
    # 1. MANIPULADORAS - Agrupación por PROGRAMA AL QUE PERTENECE
    st.header("Agrupación por Programa (Manipuladoras)")
    
    if manipuladoras_programa_col and not manipuladoras_filtradas.empty:
        # Normalizar la columna para el conteo
        manipuladoras_filtradas['programa_normalizado'] = manipuladoras_filtradas[manipuladoras_programa_col]
        
        # Contar por programa
        conteo_programas = manipuladoras_filtradas['programa_normalizado'].value_counts().reset_index()
        conteo_programas.columns = ['Programa', 'Total']
        
        # Ordenar por programa
        conteo_programas = conteo_programas.sort_values('Programa')
        # Mostrar conteo
        if len(conteo_programas) > 0:
            st.dataframe(conteo_programas, use_container_width=True)
        else:
            st.warning("No hay datos de programas disponibles con los filtros seleccionados.")
    else:
        st.warning("No hay datos disponibles de Manipuladoras o falta la columna de programa.")
    
    # 2. APRENDICES - Agrupación por AREA
    st.header("Agrupación por Área (Aprendices)")
    
    if aprendices_area_col and not aprendices_filtrados.empty:
        # Normalizar la columna para el conteo
        aprendices_filtrados['area_normalizada'] = aprendices_filtrados[aprendices_area_col]
        
        # Contar por área
        conteo_areas_aprendices = aprendices_filtrados['area_normalizada'].value_counts().reset_index()
        conteo_areas_aprendices.columns = ['Área', 'Total']
        
        # Ordenar por área
        conteo_areas_aprendices = conteo_areas_aprendices.sort_values('Área')
        
        # Mostrar conteo
        if len(conteo_areas_aprendices) > 0:
            st.dataframe(conteo_areas_aprendices, use_container_width=True)
        else:
            st.warning("No hay datos de áreas disponibles para Aprendices con los filtros seleccionados.")
    else:
        st.warning("No hay datos disponibles de Aprendices o falta la columna de área.")
    
    # 3. PLANTA - Agrupación por AREA (excluyendo BUGA)
    st.header("Agrupación por Área (Planta, excluyendo BUGA)")

    if planta_area_col and not planta_filtrada.empty:
        # Normalizar la columna para el conteo
        planta_filtrada['area_normalizada'] = planta_filtrada[planta_area_col]
        
        # Excluir las áreas que contienen BUGA
        planta_sin_buga = planta_filtrada[
            ~planta_filtrada['area_normalizada'].str.contains('BUGA', case=False, na=False)
        ]
        
        # Contar por área
        conteo_areas_planta = planta_sin_buga['area_normalizada'].value_counts().reset_index()
        conteo_areas_planta.columns = ['Área', 'Total']
        
        # Ordenar por área
        conteo_areas_planta = conteo_areas_planta.sort_values('Área')
        
        # Mostrar conteo
        if len(conteo_areas_planta) > 0:
            # Agregar una fila con el total
            total_row = pd.DataFrame({
                'Área': ['TOTAL'],
                'Total': [conteo_areas_planta['Total'].sum()]
            })
            
            # Concatenar con la tabla original
            conteo_areas_planta_con_total = pd.concat([conteo_areas_planta, total_row], ignore_index=True)
            
            # Mostrar la tabla con el total
            st.dataframe(conteo_areas_planta_con_total, use_container_width=True)
        else:
            st.warning("No hay datos de áreas disponibles para Planta (excluyendo BUGA) con los filtros seleccionados.")
    else:
        st.warning("No hay datos disponibles de Planta o falta la columna de área.")    
    
    # 4. PLANTA - Filtrado específico para BUGA
    st.header("Personal en BUGA (Planta)")
    
    if planta_area_col and not planta_filtrada.empty:
        # Filtrar registros que contengan 'BUGA'
        planta_buga = planta_filtrada[
            planta_filtrada['area_normalizada'].str.contains('BUGA', case=False, na=False)
        ]
        
        # Contar por área específica de BUGA
        if not planta_buga.empty:
            conteo_buga = planta_buga['area_normalizada'].value_counts().reset_index()
            conteo_buga.columns = ['Área en BUGA', 'Total']
            
            # Ordenar por área
            conteo_buga = conteo_buga.sort_values('Área en BUGA')
            
            # Mostrar conteo
            st.dataframe(conteo_buga, use_container_width=True)
            
            # Mostrar total general
            st.metric("Total de Personal en BUGA", planta_buga.shape[0])
        else:
            st.warning("No se encontraron registros con BUGA en el área con los filtros seleccionados.")
    else:
        st.warning("No hay datos disponibles de Planta o falta la columna de área para filtrar BUGA.")