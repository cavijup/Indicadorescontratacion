import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import os
from datetime import datetime

# ID de la hoja de Google Sheets
try:
    SHEET_ID = st.secrets["sheet_id"]
except Exception:
    # Valor por defecto para desarrollo local
    SHEET_ID = '1OzyM4jlADde1MKU7INbtXvVOUaqD1KfZH_gFLOciwNk'

# Ruta al archivo de credenciales
CREDENTIALS_PATH = 'sheets_api.json'  # Tu archivo de credenciales en la raíz del proyecto

# Ámbito para la API de Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Función para crear el servicio de Google Sheets
def create_sheets_service():
    """
    Crea y retorna un servicio autenticado para acceder a Google Sheets.
    """
    try:
        # Intentar usar las credenciales desde los secretos de Streamlit
        import json
        from google.oauth2.service_account import Credentials
        
        # Obtener credenciales desde los secretos de Streamlit
        try:
            credentials_dict = st.secrets["gcp_service_account"]
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=SCOPES
            )
        except Exception as e:
            st.error(f"Error al obtener credenciales desde secretos: {e}")
            
            # Intentar usar el archivo local como respaldo (para desarrollo local)
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    CREDENTIALS_PATH,
                    scopes=SCOPES
                )
            except Exception as e2:
                st.error(f"Error al obtener credenciales desde archivo local: {e2}")
                return None
        
        # Construir el servicio de Google Sheets
        service = build('sheets', 'v4', credentials=credentials)
        
        return service
    except Exception as e:
        st.error(f"Error al crear el servicio de Google Sheets: {e}")
        return None

# Función para cargar los datos de la hoja "Planta"
@st.cache_data(ttl=3600)  # Caché durante 1 hora
def load_planta_data():
    """
    Carga los datos de la hoja 'Planta' y los retorna como un DataFrame de pandas.
    """
    try:
        # Obtener servicio
        service = create_sheets_service()
        if service is None:
            return pd.DataFrame()
        
        # Rango de datos a obtener (ajustar según tamaño de la hoja)
        range_name = 'Planta!A1:Z1000'
        
        # Llamar a la API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=range_name
        ).execute()
        
        # Obtener valores
        values = result.get('values', [])
        if not values:
            st.warning('No se encontraron datos en la hoja Planta.')
            return pd.DataFrame()
        
        # Convertir a DataFrame
        headers = values[0]
        data = values[1:]
        df = pd.DataFrame(data, columns=headers)
        
        # Eliminar filas que estén completamente vacías
        df = df.replace('', pd.NA)
        df = df.dropna(how='all')
        
        # Asegurar que las columnas necesarias tengan nombres consistentes
        if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in df.columns:
            df['tipo_novedad'] = df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        
        # Fechas de ingreso y retiro
        if 'FECHA DE INGRESO (AAAAMMDD)' in df.columns:
            df['fecha_ingreso'] = df['FECHA DE INGRESO (AAAAMMDD)']
            # Convertir formato de fecha si es posible
            try:
                df['fecha_ingreso'] = pd.to_datetime(df['fecha_ingreso'], format='%Y%m%d', errors='coerce')
            except:
                pass
        
        if 'FECHA DE RETIRO (AAAAMMDD)' in df.columns:
            df['fecha_retiro'] = df['FECHA DE RETIRO (AAAAMMDD)']
            # Convertir formato de fecha si es posible
            try:
                df['fecha_retiro'] = pd.to_datetime(df['fecha_retiro'], format='%Y%m%d', errors='coerce')
            except:
                pass
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos de Planta: {e}")
        # Intentar cargar desde copia local si existe
        try:
            backup_path = os.path.join('data_backup', 'planta_backup.csv')
            if os.path.exists(backup_path):
                return pd.read_csv(backup_path)
        except:
            pass
        return pd.DataFrame()

# Función para cargar los datos de la hoja "Manipuladoras"
@st.cache_data(ttl=3600)  # Caché durante 1 hora
def load_manipuladoras_data():
    """
    Carga los datos de la hoja 'Manipuladoras' y los retorna como un DataFrame de pandas.
    """
    try:
        # Obtener servicio
        service = create_sheets_service()
        if service is None:
            return pd.DataFrame()
        
        # Rango de datos a obtener (ajustar según tamaño de la hoja)
        range_name = 'Manipuladoras!A1:Z1000'
        
        # Llamar a la API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=range_name
        ).execute()
        
        # Obtener valores
        values = result.get('values', [])
        if not values:
            st.warning('No se encontraron datos en la hoja Manipuladoras.')
            return pd.DataFrame()
        
        # Convertir a DataFrame
        headers = values[0]
        data = values[1:]
        df = pd.DataFrame(data, columns=headers)
        
        # Eliminar filas que estén completamente vacías
        df = df.replace('', pd.NA)
        df = df.dropna(how='all')
        
        # Asegurar que las columnas necesarias tengan nombres consistentes
        if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in df.columns:
            df['tipo_novedad'] = df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        
        # Fechas de ingreso y retiro
        if 'FECHA DE INGRESO (AAAAMMDD)' in df.columns:
            df['fecha_ingreso'] = df['FECHA DE INGRESO (AAAAMMDD)']
            # Convertir formato de fecha si es posible
            try:
                df['fecha_ingreso'] = pd.to_datetime(df['fecha_ingreso'], format='%Y%m%d', errors='coerce')
            except:
                pass
        
        if 'FECHA DE RETIRO (AAAAMMDD)' in df.columns:
            df['fecha_retiro'] = df['FECHA DE RETIRO (AAAAMMDD)']
            # Convertir formato de fecha si es posible
            try:
                df['fecha_retiro'] = pd.to_datetime(df['fecha_retiro'], format='%Y%m%d', errors='coerce')
            except:
                pass
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos de Manipuladoras: {e}")
        # Intentar cargar desde copia local si existe
        try:
            backup_path = os.path.join('data_backup', 'manipuladoras_backup.csv')
            if os.path.exists(backup_path):
                return pd.read_csv(backup_path)
        except:
            pass
        return pd.DataFrame()
    
# Función para cargar los datos de la hoja "Aprendices"
@st.cache_data(ttl=3600)  # Caché durante 1 hora
def load_aprendices_data():
    """
    Carga los datos de la hoja 'Aprendices' y los retorna como un DataFrame de pandas.
    """
    try:
        # Obtener servicio
        service = create_sheets_service()
        if service is None:
            return pd.DataFrame()
        
        # Rango de datos a obtener (ajustar según tamaño de la hoja)
        range_name = 'Aprendices!A1:AZ1000'
        
        # Llamar a la API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=range_name
        ).execute()
        
        # Obtener valores
        values = result.get('values', [])
        if not values:
            st.warning('No se encontraron datos en la hoja Aprendices.')
            return pd.DataFrame()
        
        # Convertir a DataFrame
        headers = values[0]
        data = values[1:]
        df = pd.DataFrame(data, columns=headers)
        
        # Eliminar filas que estén completamente vacías
        df = df.replace('', pd.NA)
        df = df.dropna(how='all')
        
        # Asegurar que las columnas necesarias tengan nombres consistentes
        if 'TIPO DE NOVEDAD' in df.columns:
            df['tipo_novedad'] = df['TIPO DE NOVEDAD']
        
        # Fechas de ingreso y retiro
        if 'FECHA DE INGRESO' in df.columns:
            df['fecha_ingreso'] = df['FECHA DE INGRESO']
            # Convertir formato de fecha si es posible
            try:
                df['fecha_ingreso'] = pd.to_datetime(df['fecha_ingreso'], format='%Y%m%d', errors='coerce')
            except:
                pass
        
        if 'FECHA RETIRO' in df.columns:
            df['fecha_retiro'] = df['FECHA RETIRO']
            # Convertir formato de fecha si es posible
            try:
                df['fecha_retiro'] = pd.to_datetime(df['fecha_retiro'], format='%Y%m%d', errors='coerce')
            except:
                pass
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos de Aprendices: {e}")
        # Intentar cargar desde copia local si existe
        try:
            backup_path = os.path.join('data_backup', 'aprendices_backup.csv')
            if os.path.exists(backup_path):
                return pd.read_csv(backup_path)
        except:
            pass
        return pd.DataFrame()

# Modificar la función load_all_data para incluir Aprendices
def load_all_data():
    """
    Carga los datos de las hojas Planta, Manipuladoras y Aprendices y los retorna como un diccionario de DataFrames.
    """
    planta_df = load_planta_data()
    manipuladoras_df = load_manipuladoras_data()
    aprendices_df = load_aprendices_data()  # Nueva línea
    
    return {
        'planta': planta_df,
        'manipuladoras': manipuladoras_df,
        'aprendices': aprendices_df  # Nueva línea
    }

def get_unique_tipos_novedad():
    """
    Retorna una lista con los valores únicos de tipo de novedad de todas las tablas.
    """
    data_dict = load_all_data()
    planta_df = data_dict['planta']
    manipuladoras_df = data_dict['manipuladoras']
    aprendices_df = data_dict['aprendices']  # Añadido
    
    tipos_planta = []
    tipos_manipuladoras = []
    tipos_aprendices = []  # Añadido
    
    if 'tipo_novedad' in planta_df.columns:
        tipos_planta = planta_df['tipo_novedad'].dropna().unique().tolist()
    elif 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in planta_df.columns:
        tipos_planta = planta_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)'].dropna().unique().tolist()
    
    if 'tipo_novedad' in manipuladoras_df.columns:
        tipos_manipuladoras = manipuladoras_df['tipo_novedad'].dropna().unique().tolist()
    elif 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in manipuladoras_df.columns:
        tipos_manipuladoras = manipuladoras_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)'].dropna().unique().tolist()
    
    # Añadido: Buscar en aprendices
    if 'tipo_novedad' in aprendices_df.columns:
        tipos_aprendices = aprendices_df['tipo_novedad'].dropna().unique().tolist()
    elif 'TIPO DE NOVEDAD' in aprendices_df.columns:
        tipos_aprendices = aprendices_df['TIPO DE NOVEDAD'].dropna().unique().tolist()
    
    # Combinar y eliminar duplicados
    tipos_combinados = list(set(tipos_planta + tipos_manipuladoras + tipos_aprendices))
    
    return sorted(tipos_combinados)

# Función para filtrar datos por tipo de novedad
def filter_data_by_novedad(data_dict, tipos_novedad_seleccionados):
    """
    Filtra los DataFrames por tipos de novedad seleccionados.
    """
    planta_df = data_dict['planta'].copy()
    manipuladoras_df = data_dict['manipuladoras'].copy()
    aprendices_df = data_dict['aprendices'].copy()  # Añadido
    
    # Filtrar planta
    if 'tipo_novedad' in planta_df.columns:
        planta_df = planta_df[planta_df['tipo_novedad'].isin(tipos_novedad_seleccionados)]
    elif 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in planta_df.columns:
        planta_df = planta_df[planta_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)'].isin(tipos_novedad_seleccionados)]
    
    # Filtrar manipuladoras
    if 'tipo_novedad' in manipuladoras_df.columns:
        manipuladoras_df = manipuladoras_df[manipuladoras_df['tipo_novedad'].isin(tipos_novedad_seleccionados)]
    elif 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in manipuladoras_df.columns:
        manipuladoras_df = manipuladoras_df[manipuladoras_df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)'].isin(tipos_novedad_seleccionados)]
    
    # Añadido: Filtrar aprendices
    if 'tipo_novedad' in aprendices_df.columns:
        aprendices_df = aprendices_df[aprendices_df['tipo_novedad'].isin(tipos_novedad_seleccionados)]
    elif 'TIPO DE NOVEDAD' in aprendices_df.columns:
        aprendices_df = aprendices_df[aprendices_df['TIPO DE NOVEDAD'].isin(tipos_novedad_seleccionados)]
    
    return {
        'planta': planta_df,
        'manipuladoras': manipuladoras_df,
        'aprendices': aprendices_df  # Añadido
    }

# Función para obtener rango de fechas disponibles según tipo de novedad
def get_date_range_by_novedad(data_dict, tipos_novedad_seleccionados):
    """
    Retorna el rango de fechas disponibles según el tipo de novedad seleccionado.
    """
    planta_df = data_dict['planta']
    manipuladoras_df = data_dict['manipuladoras']
    aprendices_df = data_dict['aprendices']  # Añadido
    
    fechas = []
    
    # Determinar qué columna de fecha usar
    if 'ACTIVO' in tipos_novedad_seleccionados or 'CASO ESPECIAL' in tipos_novedad_seleccionados:
        # Usar fechas de ingreso
        if 'fecha_ingreso' in planta_df.columns:
            fechas.extend(planta_df['fecha_ingreso'].dropna().tolist())
        if 'fecha_ingreso' in manipuladoras_df.columns:
            fechas.extend(manipuladoras_df['fecha_ingreso'].dropna().tolist())
        if 'fecha_ingreso' in aprendices_df.columns:  # Añadido
            fechas.extend(aprendices_df['fecha_ingreso'].dropna().tolist())
    
    if 'RETIRADO' in tipos_novedad_seleccionados:
        # Usar fechas de retiro
        if 'fecha_retiro' in planta_df.columns:
            fechas.extend(planta_df['fecha_retiro'].dropna().tolist())
        if 'fecha_retiro' in manipuladoras_df.columns:
            fechas.extend(manipuladoras_df['fecha_retiro'].dropna().tolist())
        if 'fecha_retiro' in aprendices_df.columns:  # Añadido
            fechas.extend(aprendices_df['fecha_retiro'].dropna().tolist())
    
    # Convertir a fechas válidas si no son datetime
    valid_fechas = []
    for fecha in fechas:
        if isinstance(fecha, pd.Timestamp) or isinstance(fecha, datetime):
            valid_fechas.append(fecha)
        else:
            try:
                fecha_dt = pd.to_datetime(fecha, format='%Y%m%d', errors='coerce')
                if not pd.isna(fecha_dt):
                    valid_fechas.append(fecha_dt)
            except:
                pass
    
    if not valid_fechas:
        # Retornar un rango predeterminado si no hay fechas
        today = pd.Timestamp.now()
        return today - pd.Timedelta(days=365), today
    
    min_date = min(valid_fechas)
    max_date = max(valid_fechas)
    
    return min_date, max_date

# Función para filtrar datos por rango de fechas
def filter_data_by_date_range(data_dict, tipos_novedad_seleccionados, date_range):
    """
    Filtra los DataFrames por rango de fechas según el tipo de novedad.
    """
    planta_df = data_dict['planta'].copy()
    manipuladoras_df = data_dict['manipuladoras'].copy()
    aprendices_df = data_dict['aprendices'].copy()  # Añadido
    
    fecha_min, fecha_max = date_range
    
    # Crear máscaras para cada DataFrame
    planta_mask = pd.Series(False, index=planta_df.index)
    manipuladoras_mask = pd.Series(False, index=manipuladoras_df.index)
    aprendices_mask = pd.Series(False, index=aprendices_df.index)  # Añadido
    
    # Aplicar filtros según el tipo de novedad seleccionado
    if 'ACTIVO' in tipos_novedad_seleccionados or 'CASO ESPECIAL' in tipos_novedad_seleccionados:
        # Filtrar por fecha de ingreso para ACTIVO o CASO ESPECIAL
        if 'fecha_ingreso' in planta_df.columns:
            planta_mask = planta_mask | ((planta_df['fecha_ingreso'] >= fecha_min) & 
                                        (planta_df['fecha_ingreso'] <= fecha_max))
        
        if 'fecha_ingreso' in manipuladoras_df.columns:
            manipuladoras_mask = manipuladoras_mask | ((manipuladoras_df['fecha_ingreso'] >= fecha_min) & 
                                                     (manipuladoras_df['fecha_ingreso'] <= fecha_max))
        
        # Añadido: Filtrar aprendices por fecha de ingreso
        if 'fecha_ingreso' in aprendices_df.columns:
            aprendices_mask = aprendices_mask | ((aprendices_df['fecha_ingreso'] >= fecha_min) & 
                                               (aprendices_df['fecha_ingreso'] <= fecha_max))
    
    if 'RETIRADO' in tipos_novedad_seleccionados:
        # Filtrar por fecha de retiro para RETIRADO
        if 'fecha_retiro' in planta_df.columns:
            planta_mask = planta_mask | ((planta_df['fecha_retiro'] >= fecha_min) & 
                                        (planta_df['fecha_retiro'] <= fecha_max))
        
        if 'fecha_retiro' in manipuladoras_df.columns:
            manipuladoras_mask = manipuladoras_mask | ((manipuladoras_df['fecha_retiro'] >= fecha_min) & 
                                                     (manipuladoras_df['fecha_retiro'] <= fecha_max))
        
        # Añadido: Filtrar aprendices por fecha de retiro
        if 'fecha_retiro' in aprendices_df.columns:
            aprendices_mask = aprendices_mask | ((aprendices_df['fecha_retiro'] >= fecha_min) & 
                                               (aprendices_df['fecha_retiro'] <= fecha_max))
    
    # Aplicar las máscaras
    planta_df = planta_df[planta_mask]
    manipuladoras_df = manipuladoras_df[manipuladoras_mask]
    aprendices_df = aprendices_df[aprendices_mask]  # Añadido
    
    return {
        'planta': planta_df,
        'manipuladoras': manipuladoras_df,
        'aprendices': aprendices_df  # Añadido
    }

# Función para limpiar la caché de Streamlit
def clear_cache():
    """
    Limpia la caché de datos de Streamlit.
    """
    st.cache_data.clear()
    st.success("Caché limpiada correctamente")