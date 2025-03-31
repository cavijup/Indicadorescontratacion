import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import load_all_data

def run():
    """
    Módulo que muestra los motivos de retiro agrupados por:
    - EMPRESA (Planta, columna F)
    - PROGRAMA AL QUE PERTENECE (Manipuladoras, columna H)
    Incluye un gráfico de columnas para visualizar la cantidad de retiros por motivo.
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
    
    # Por defecto, preseleccionar "RETIRADO" ya que estamos en la página de retiros
    default_novedad = ["RETIRADO"] if "RETIRADO" in todos_tipos_novedad else todos_tipos_novedad
    
    # Multiselect para seleccionar múltiples opciones
    tipos_novedad_seleccionados = st.sidebar.multiselect(
        "Tipo de Novedad",
        options=todos_tipos_novedad,
        default=default_novedad
    )
    
    # Si no hay selección, mostrar advertencia
    if not tipos_novedad_seleccionados:
        st.sidebar.warning("Por favor, seleccione al menos un tipo de novedad.")
        tipos_novedad_seleccionados = default_novedad  # Usar "RETIRADO" como respaldo
    
    # 2. FILTRO DE FECHAS
    st.sidebar.subheader("Rango de Fechas")
    
    # Preparar las fechas en los DataFrames para el filtrado
    for df_name, df in [('manipuladoras', manipuladoras_df), ('planta', planta_df)]:
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
        for df in [manipuladoras_df, planta_df]:
            if 'fecha_ingreso' in df.columns:
                fechas.extend(df['fecha_ingreso'].dropna().tolist())
    
    if "RETIRADO" in tipos_novedad_seleccionados:
        st.sidebar.text("Se usarán Fechas de Retiro para RETIRADO")
        for df in [manipuladoras_df, planta_df]:
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
        key="date_range_retiros"
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
    
    # ---------- MOSTRAR INFORMACIÓN DE RESULTADOS ----------
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Registros filtrados en Manipuladoras: {len(manipuladoras_filtradas)}")
    with col2:
        st.info(f"Registros filtrados en Planta: {len(planta_filtrada)}")

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
    planta_motivo_retiro_col = encontrar_columna_por_posicion(
        planta_filtrada, 
        10,  # Posición K
        ['MOTIVO DEL RETIRO', 'Motivo del Retiro', 'MOTIVO RETIRO']
    )
    
    planta_empresa_col = encontrar_columna_por_posicion(
        planta_filtrada, 
        5,  # Posición F
        ['EMPRESA', 'Empresa']
    )
    
    manipuladoras_motivo_retiro_col = encontrar_columna_por_posicion(
        manipuladoras_filtradas, 
        17,  # Posición R
        ['MOTIVO DEL RETIRO', 'Motivo del Retiro', 'MOTIVO RETIRO']
    )
    
    manipuladoras_programa_col = encontrar_columna_por_posicion(
        manipuladoras_filtradas, 
        7,  # Posición H
        ['PROGRAMA AL QUE PERTENECE', 'Programa al que Pertenece', 'PROGRAMA']
    )
    
    # Mostrar advertencia si no se encuentran las columnas
    missing_cols = []
    if not planta_motivo_retiro_col:
        missing_cols.append("MOTIVO DEL RETIRO (Planta, posición K)")
    if not planta_empresa_col:
        missing_cols.append("EMPRESA (Planta, posición F)")
    if not manipuladoras_motivo_retiro_col:
        missing_cols.append("MOTIVO DEL RETIRO (Manipuladoras, posición R)")
    if not manipuladoras_programa_col:
        missing_cols.append("PROGRAMA AL QUE PERTENECE (Manipuladoras, posición H)")
    
    if missing_cols:
        st.warning(f"No se encontraron las siguientes columnas: {', '.join(missing_cols)}")
        st.info("Por favor, verifica los nombres o posiciones de las columnas en los datos.")
    
    # ---------- CREAR TABLAS DE AGRUPACIÓN ----------
    # 1. PLANTA - Motivos de retiro por Empresa
    st.header("Motivos de Retiro por Empresa (Planta)")
    
    if planta_motivo_retiro_col and planta_empresa_col and not planta_filtrada.empty:
        # Normalizar las columnas para el conteo
        planta_filtrada['motivo_retiro_normalizado'] = planta_filtrada[planta_motivo_retiro_col]
        planta_filtrada['empresa_normalizada'] = planta_filtrada[planta_empresa_col]
        
        # Filtrar solo registros que tengan motivo de retiro
        planta_con_motivo = planta_filtrada.dropna(subset=['motivo_retiro_normalizado'])
        
        if not planta_con_motivo.empty:
            # Agrupar por empresa y motivo de retiro
            conteo_planta = planta_con_motivo.groupby(['empresa_normalizada', 'motivo_retiro_normalizado']).size().reset_index()
            conteo_planta.columns = ['Empresa', 'Motivo de Retiro', 'Total']
            
            # Ordenar por empresa y total (descendente)
            conteo_planta = conteo_planta.sort_values(['Empresa', 'Total'], ascending=[True, False])
            
            # Mostrar la tabla
            st.dataframe(conteo_planta, use_container_width=True)
            
            # Crear un dataframe para el total por motivo (para el gráfico)
            total_por_motivo_planta = planta_con_motivo['motivo_retiro_normalizado'].value_counts().reset_index()
            total_por_motivo_planta.columns = ['Motivo de Retiro', 'Total']
            total_por_motivo_planta['Origen'] = 'Planta'
        else:
            st.warning("No hay datos de retiros disponibles en Planta con los filtros seleccionados.")
            total_por_motivo_planta = pd.DataFrame(columns=['Motivo de Retiro', 'Total', 'Origen'])
    else:
        st.warning("No hay datos disponibles de Planta o faltan las columnas necesarias.")
        total_por_motivo_planta = pd.DataFrame(columns=['Motivo de Retiro', 'Total', 'Origen'])
    
    # 2. MANIPULADORAS - Motivos de retiro por Programa
    st.header("Motivos de Retiro por Programa (Manipuladoras)")
    
    if manipuladoras_motivo_retiro_col and manipuladoras_programa_col and not manipuladoras_filtradas.empty:
        # Normalizar las columnas para el conteo
        manipuladoras_filtradas['motivo_retiro_normalizado'] = manipuladoras_filtradas[manipuladoras_motivo_retiro_col]
        manipuladoras_filtradas['programa_normalizado'] = manipuladoras_filtradas[manipuladoras_programa_col]
        
        # Filtrar solo registros que tengan motivo de retiro
        manipuladoras_con_motivo = manipuladoras_filtradas.dropna(subset=['motivo_retiro_normalizado'])
        
        if not manipuladoras_con_motivo.empty:
            # Agrupar por programa y motivo de retiro
            conteo_manipuladoras = manipuladoras_con_motivo.groupby(['programa_normalizado', 'motivo_retiro_normalizado']).size().reset_index()
            conteo_manipuladoras.columns = ['Programa', 'Motivo de Retiro', 'Total']
            
            # Ordenar por programa y total (descendente)
            conteo_manipuladoras = conteo_manipuladoras.sort_values(['Programa', 'Total'], ascending=[True, False])
            
            # Mostrar la tabla
            st.dataframe(conteo_manipuladoras, use_container_width=True)
            
            # Crear un dataframe para el total por motivo (para el gráfico)
            total_por_motivo_manipuladoras = manipuladoras_con_motivo['motivo_retiro_normalizado'].value_counts().reset_index()
            total_por_motivo_manipuladoras.columns = ['Motivo de Retiro', 'Total']
            total_por_motivo_manipuladoras['Origen'] = 'Manipuladoras'
        else:
            st.warning("No hay datos de retiros disponibles en Manipuladoras con los filtros seleccionados.")
            total_por_motivo_manipuladoras = pd.DataFrame(columns=['Motivo de Retiro', 'Total', 'Origen'])
    else:
        st.warning("No hay datos disponibles de Manipuladoras o faltan las columnas necesarias.")
        total_por_motivo_manipuladoras = pd.DataFrame(columns=['Motivo de Retiro', 'Total', 'Origen'])
    
    # ---------- CREAR GRÁFICO DE COLUMNAS ----------
    st.header("Gráfico de Motivos de Retiro")
    
    # Combinar los datos de ambas fuentes para el gráfico
    if not total_por_motivo_planta.empty or not total_por_motivo_manipuladoras.empty:
        # Concatenar los dataframes
        total_por_motivo = pd.concat([total_por_motivo_planta, total_por_motivo_manipuladoras], ignore_index=True)
        
        # Agrupar por motivo de retiro y origen
        pivot_motivos = pd.pivot_table(
            total_por_motivo,
            values='Total',
            index='Motivo de Retiro',
            columns='Origen',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Asegurar que existan las columnas para ambos orígenes
        if 'Planta' not in pivot_motivos.columns:
            pivot_motivos['Planta'] = 0
        if 'Manipuladoras' not in pivot_motivos.columns:
            pivot_motivos['Manipuladoras'] = 0
        
        # Calcular el total general
        pivot_motivos['Total General'] = pivot_motivos['Planta'] + pivot_motivos['Manipuladoras']
        
        # Ordenar por total general (descendente)
        pivot_motivos = pivot_motivos.sort_values('Total General', ascending=False)
        
        # Mostrar tabla resumen
        st.subheader("Tabla resumen de motivos de retiro")
        st.dataframe(pivot_motivos, use_container_width=True)
        
        # Crear un DataFrame para el gráfico con formato largo (long format)
        graph_data = pd.melt(
            pivot_motivos, 
            id_vars=['Motivo de Retiro'], 
            value_vars=['Planta', 'Manipuladoras'],
            var_name='Origen', 
            value_name='Cantidad'
        )
        
        # Crear gráfico de barras agrupadas
        fig = px.bar(
            graph_data,
            x='Motivo de Retiro',
            y='Cantidad',
            color='Origen',
            barmode='group',
            title='Cantidad de Retiros por Motivo',
            labels={'Cantidad': 'Número de Retiros', 'Motivo de Retiro': 'Motivo', 'Origen': 'Origen de Datos'},
            height=600
        )
        
        # Personalizar el diseño
        fig.update_layout(
            xaxis_title="Motivo de Retiro",
            yaxis_title="Cantidad de Retiros",
            legend_title="Origen de Datos",
            xaxis={'categoryorder':'total descending'},
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Crear un gráfico para el total general
        total_general = pivot_motivos[['Motivo de Retiro', 'Total General']].sort_values('Total General', ascending=False)
        
        fig_total = px.bar(
            total_general,
            x='Motivo de Retiro',
            y='Total General',
            title='Total de Retiros por Motivo (Ambas Fuentes)',
            labels={'Total General': 'Número de Retiros', 'Motivo de Retiro': 'Motivo'},
            height=400,
            color='Total General',
            color_continuous_scale='Viridis'
        )
        
        # Personalizar el diseño
        fig_total.update_layout(
            xaxis_title="Motivo de Retiro",
            yaxis_title="Total de Retiros",
            xaxis={'categoryorder':'total descending'},
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig_total, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para generar el gráfico de motivos de retiro.")