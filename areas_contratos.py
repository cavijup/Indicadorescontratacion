import streamlit as st
import pandas as pd
from utils import load_all_data

def run():
    """
    Módulo que muestra una tabla agrupada por Área y Tipo de Contrato,
    combinando datos de las tablas Manipuladoras y Planta.
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
        default=["ACTIVO"]  # Por defecto, mostrar solo activos
    )
    
    # Si no hay selección, mostrar advertencia
    if not tipos_novedad_seleccionados:
        st.sidebar.warning("Por favor, seleccione al menos un tipo de novedad.")
        tipos_novedad_seleccionados = ["ACTIVO"]  # Usar "ACTIVO" como respaldo
    
    # ---------- APLICAR FILTROS A LOS DATOS ----------
    manipuladoras_filtradas = manipuladoras_df.copy()
    planta_filtrada = planta_df.copy()
    
    # Filtrar por tipo de novedad
    if 'tipo_novedad' in manipuladoras_filtradas.columns:
        manipuladoras_filtradas = manipuladoras_filtradas[
            manipuladoras_filtradas['tipo_novedad'].isin(tipos_novedad_seleccionados)
        ]
    
    if 'tipo_novedad' in planta_filtrada.columns:
        planta_filtrada = planta_filtrada[
            planta_filtrada['tipo_novedad'].isin(tipos_novedad_seleccionados)
        ]
    
    # ---------- PROCESAMIENTO PARA LA TABLA DE ÁREAS POR TIPO DE CONTRATO ----------
    # Verificar que existan las columnas necesarias en el DataFrame planta
    planta_area_col = None
    planta_contrato_col = None
    manipuladoras_area_col = None
    manipuladoras_contrato_col = None
    
    # Buscar columnas en Planta - Posición N (AREA) y M (TIPO DE CONTRATO)
    for col_idx, col_name in enumerate(planta_filtrada.columns):
        if col_idx == 13:  # M es posición 13 (0-based indexing)
            planta_contrato_col = col_name
        elif col_idx == 14:  # N es posición 14 (0-based indexing)
            planta_area_col = col_name
    
    # Buscar columnas en Manipuladoras - Posición F (AREA) y T (TIPO DE CONTRATO)
    for col_idx, col_name in enumerate(manipuladoras_filtradas.columns):
        if col_idx == 5:  # F es posición 5 (0-based indexing)
            manipuladoras_area_col = col_name
        elif col_idx == 19:  # T es posición 19 (0-based indexing)
            manipuladoras_contrato_col = col_name
    
    # Si no se encuentran las columnas por posición, intentar con nombres conocidos
    if not planta_area_col:
        possible_area_cols = ['AREA', 'ÁREA', 'Area', 'Área']
        for col in possible_area_cols:
            if col in planta_filtrada.columns:
                planta_area_col = col
                break
    
    if not planta_contrato_col:
        possible_contract_cols = ['TIPO DE CONTRATO', 'Tipo de Contrato', 'TIPO CONTRATO']
        for col in possible_contract_cols:
            if col in planta_filtrada.columns:
                planta_contrato_col = col
                break
    
    if not manipuladoras_area_col:
        possible_area_cols = ['AREA', 'ÁREA', 'Area', 'Área']
        for col in possible_area_cols:
            if col in manipuladoras_filtradas.columns:
                manipuladoras_area_col = col
                break
    
    if not manipuladoras_contrato_col:
        possible_contract_cols = ['TIPO DE CONTRATO', 'Tipo de Contrato', 'TIPO CONTRATO']
        for col in possible_contract_cols:
            if col in manipuladoras_filtradas.columns:
                manipuladoras_contrato_col = col
                break
    
    # Mostrar advertencia si no se encuentran las columnas
    missing_cols = []
    if not planta_area_col:
        missing_cols.append("Área (Planta)")
    if not planta_contrato_col:
        missing_cols.append("Tipo de Contrato (Planta)")
    if not manipuladoras_area_col:
        missing_cols.append("Área (Manipuladoras)")
    if not manipuladoras_contrato_col:
        missing_cols.append("Tipo de Contrato (Manipuladoras)")
    
    if missing_cols:
        st.warning(f"No se encontraron las siguientes columnas: {', '.join(missing_cols)}")
        st.info("Por favor, verifica los nombres o posiciones de las columnas en los datos.")
    
    # Lista para almacenar resultados
    resultados = []
    
    # Procesar datos de Planta
    if planta_area_col and planta_contrato_col:
        # Crear columnas normalizadas para agrupar
        planta_filtrada['area_normalizada'] = planta_filtrada[planta_area_col]
        planta_filtrada['contrato_normalizado'] = planta_filtrada[planta_contrato_col]
        
        # Contar registros por área y tipo de contrato
        planta_conteo = planta_filtrada.groupby(['area_normalizada', 'contrato_normalizado']).size().reset_index()
        planta_conteo.columns = ['Área', 'Tipo de Contrato', 'Total']
        planta_conteo['Origen'] = 'Planta'
        
        resultados.append(planta_conteo)
    
    # Procesar datos de Manipuladoras
    if manipuladoras_area_col and manipuladoras_contrato_col:
        # Crear columnas normalizadas para agrupar
        manipuladoras_filtradas['area_normalizada'] = manipuladoras_filtradas[manipuladoras_area_col]
        manipuladoras_filtradas['contrato_normalizado'] = manipuladoras_filtradas[manipuladoras_contrato_col]
        
        # Contar registros por área y tipo de contrato
        manipuladoras_conteo = manipuladoras_filtradas.groupby(['area_normalizada', 'contrato_normalizado']).size().reset_index()
        manipuladoras_conteo.columns = ['Área', 'Tipo de Contrato', 'Total']
        manipuladoras_conteo['Origen'] = 'Manipuladoras'
        
        resultados.append(manipuladoras_conteo)
    
    # Combinar resultados
    if resultados:
        # Concatenar los DataFrames
        conteo_areas_contrato = pd.concat(resultados, ignore_index=True)
        
        # Mostrar tabla de conteo por área y tipo de contrato
        st.header("Conteo por Área y Tipo de Contrato")
        
        # Incluir selector para mostrar origen (Planta/Manipuladoras/Ambos)
        origen_seleccionado = st.selectbox(
            "Mostrar datos de:",
            options=["Ambos", "Planta", "Manipuladoras"]
        )
        
        # Filtrar por origen seleccionado
        if origen_seleccionado == "Planta":
            conteo_filtrado = conteo_areas_contrato[conteo_areas_contrato["Origen"] == "Planta"]
        elif origen_seleccionado == "Manipuladoras":
            conteo_filtrado = conteo_areas_contrato[conteo_areas_contrato["Origen"] == "Manipuladoras"]
        else:
            # Si es "Ambos", agrupar nuevamente para combinar totales
            conteo_filtrado = conteo_areas_contrato.groupby(['Área', 'Tipo de Contrato']).sum().reset_index()
        
        # Ordenar por Área y luego por Tipo de Contrato
        conteo_filtrado = conteo_filtrado.sort_values(['Área', 'Tipo de Contrato'])
        
        # Mostrar la tabla
        if len(conteo_filtrado) > 0:
            st.dataframe(conteo_filtrado, use_container_width=True)
        else:
            st.warning("No hay datos disponibles con los filtros seleccionados.")
    else:
        st.error("No se pudieron procesar los datos debido a columnas faltantes.")