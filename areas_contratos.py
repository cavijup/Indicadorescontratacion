import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import load_all_data

def run():
    """
    Módulo que muestra tablas agrupadas por Tipo de Contrato para Planta y Aprendices,
    por Área y Tipo de Contrato para Manipuladoras, y una tabla resumen global.
    """
    # Cargar datos
    with st.spinner("Cargando datos..."):
        data_dict = load_all_data()
        
        # Extraer los DataFrames
        manipuladoras_df = data_dict['manipuladoras'].copy()
        planta_df = data_dict['planta'].copy() 
        aprendices_df = data_dict['aprendices'].copy()  # Ahora cargamos la tabla real
    
    # Verificar si la tabla de aprendices está vacía
    if aprendices_df.empty:
        st.warning("No se encontraron datos en la tabla Aprendices. Por favor, verifica la hoja de Google Sheets.")
    
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
    
    # 2. FILTRO DE FECHAS (Igual que en la primera página)
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
        key="date_range_areas"
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
    planta_contrato_col = encontrar_columna_por_posicion(
        planta_filtrada, 
        12,  # Posición M
        ['TIPO DE CONTRATO', 'Tipo de Contrato', 'TIPO CONTRATO']
    )
    
    manipuladoras_area_col = encontrar_columna_por_posicion(
        manipuladoras_filtradas, 
        5,  # Posición F
        ['AREA', 'ÁREA', 'Area', 'Área']
    )
    
    manipuladoras_contrato_col = encontrar_columna_por_posicion(
        manipuladoras_filtradas, 
        19,  # Posición T
        ['TIPO DE CONTRATO', 'Tipo de Contrato', 'TIPO CONTRATO']
    )
    
    aprendices_contrato_col = encontrar_columna_por_posicion(
        aprendices_filtrados, 
        39,  # Posición An
        ['TIPO DE CONTRATO', 'Tipo de Contrato', 'TIPO CONTRATO']
    )
    
    # Mostrar advertencia si no se encuentran las columnas
    missing_cols = []
    if not planta_contrato_col:
        missing_cols.append("Tipo de Contrato (Planta, posición M)")
    if not manipuladoras_area_col:
        missing_cols.append("Área (Manipuladoras, posición F)")
    if not manipuladoras_contrato_col:
        missing_cols.append("Tipo de Contrato (Manipuladoras, posición T)")
    if not aprendices_contrato_col:
        missing_cols.append("Tipo de Contrato (Aprendices, posición An)")
    
    if missing_cols:
        st.warning(f"No se encontraron las siguientes columnas: {', '.join(missing_cols)}")
        st.info("Por favor, verifica los nombres o posiciones de las columnas en los datos.")
    
    # ---------- FUNCIONES PARA CREAR TABLAS ----------
    def crear_tabla_por_contrato(df, col_contrato, titulo, origen):
        """Crea una tabla de conteo por tipo de contrato."""
        st.header(titulo)
        
        if col_contrato and not df.empty:
            # Crear columna normalizada para agrupar
            df['contrato_normalizado'] = df[col_contrato]
            
            # Contar registros por tipo de contrato
            conteo = df['contrato_normalizado'].value_counts().reset_index()
            conteo.columns = ['Tipo de Contrato', 'Total']
            conteo['Origen'] = origen
            
            # Ordenar por tipo de contrato
            conteo = conteo.sort_values('Tipo de Contrato')
            
            # Mostrar la tabla
            if len(conteo) > 0:
                st.dataframe(conteo, use_container_width=True)
                return conteo
            else:
                st.warning(f"No hay datos disponibles de {origen} con los filtros seleccionados.")
                return pd.DataFrame(columns=['Tipo de Contrato', 'Total', 'Origen'])
        else:
            st.warning(f"No hay datos disponibles de {origen} o falta la columna de tipo de contrato.")
            return pd.DataFrame(columns=['Tipo de Contrato', 'Total', 'Origen'])
    
    def crear_tabla_por_area_contrato(df, col_area, col_contrato, titulo, origen):
        """Crea una tabla de conteo por área y tipo de contrato."""
        st.header(titulo)
        
        if col_area and col_contrato and not df.empty:
            # Crear columnas normalizadas para agrupar
            df['area_normalizada'] = df[col_area]
            df['contrato_normalizado'] = df[col_contrato]
            
            # Contar registros por área y tipo de contrato
            conteo = df.groupby(['area_normalizada', 'contrato_normalizado']).size().reset_index()
            conteo.columns = ['Área', 'Tipo de Contrato', 'Total']
            conteo['Origen'] = origen
            
            # Ordenar por Área y luego por Tipo de Contrato
            conteo = conteo.sort_values(['Área', 'Tipo de Contrato'])
            
            # Mostrar la tabla
            if len(conteo) > 0:
                st.dataframe(conteo, use_container_width=True)
                
                # También crear un conteo solo por tipo de contrato para el resumen
                resumen = conteo.groupby('Tipo de Contrato')['Total'].sum().reset_index()
                resumen['Origen'] = origen
                return resumen
            else:
                st.warning(f"No hay datos disponibles de {origen} con los filtros seleccionados.")
                return pd.DataFrame(columns=['Tipo de Contrato', 'Total', 'Origen'])
        else:
            st.warning(f"No hay datos disponibles de {origen} o faltan las columnas necesarias.")
            return pd.DataFrame(columns=['Tipo de Contrato', 'Total', 'Origen'])
    
    # ---------- TABLA 1: PLANTA POR TIPO DE CONTRATO ----------
    conteo_planta = crear_tabla_por_contrato(
        planta_filtrada, 
        planta_contrato_col,
        "Conteo por Tipo de Contrato (Planta)", 
        "Planta"
    )
    
    # ---------- TABLA 2: MANIPULADORAS POR ÁREA Y TIPO DE CONTRATO ----------
    conteo_manipuladoras = crear_tabla_por_area_contrato(
        manipuladoras_filtradas,
        manipuladoras_area_col,
        manipuladoras_contrato_col,
        "Conteo por Área y Tipo de Contrato (Manipuladoras)",
        "Manipuladoras"
    )
    
    # ---------- TABLA 3: APRENDICES POR TIPO DE CONTRATO ----------
    conteo_aprendices = crear_tabla_por_contrato(
        aprendices_filtrados, 
        aprendices_contrato_col,
        "Conteo por Tipo de Contrato (Aprendices)", 
        "Aprendices"
    )
    
    # ---------- TABLA RESUMEN: TODAS LAS FUENTES ----------
    st.header("Tabla Resumen: Todos los Tipos de Contrato")
    
    # Combinar todos los conteos
    conteos = [conteo_planta, conteo_manipuladoras, conteo_aprendices]
    conteos = [c for c in conteos if not c.empty]
    
    if conteos:
        # Concatenar todos los conteos
        todos_conteos = pd.concat(conteos, ignore_index=True)
        
        # Crear pivote para mostrar una tabla más clara
        pivote = pd.pivot_table(
            todos_conteos, 
            values='Total', 
            index='Tipo de Contrato', 
            columns='Origen', 
            aggfunc='sum', 
            fill_value=0
        ).reset_index()
        
        # Asegurarse de que todas las columnas de origen existan
        for origen in ['Planta', 'Manipuladoras', 'Aprendices']:
            if origen not in pivote.columns:
                pivote[origen] = 0
        
        # Añadir columna de total
        pivote['Total General'] = pivote[['Planta', 'Manipuladoras', 'Aprendices']].sum(axis=1)
        
        # Ordenar por tipo de contrato
        pivote = pivote.sort_values('Tipo de Contrato')
        
        # Añadir una fila de totales
        totales = pd.DataFrame({
            'Tipo de Contrato': ['TOTAL'],
            'Planta': [pivote['Planta'].sum()],
            'Manipuladoras': [pivote['Manipuladoras'].sum()],
            'Aprendices': [pivote['Aprendices'].sum()],
            'Total General': [pivote['Total General'].sum()]
        })
        
        pivote = pd.concat([pivote, totales], ignore_index=True)
        
        # Mostrar la tabla resumen
        st.dataframe(pivote, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para crear la tabla resumen.")