import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
from datetime import datetime
import os

# ID de la hoja de Google Sheets
# ID de la hoja de Google Sheets
try:
    SHEET_ID = st.secrets["sheet_id"]
except Exception:
    # Valor por defecto para desarrollo local
    SHEET_ID = '1n_ziJxtJD-dBGcedIQ-2vF_tFZ71sTJw2cQj6RpvbXE'

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
        
        # CAMBIO IMPORTANTE: Eliminar filas que estén completamente vacías
        # Primero, rellenar valores vacíos con NaN
        df = df.replace('', pd.NA)
        
        # Eliminar filas donde todas las columnas son NaN
        df = df.dropna(how='all')
        
        # Procesamiento de datos (convertir fechas, etc.)
        if 'FECHA DE INGRESO (AAAAMMDD)' in df.columns:
            df['fecha_ingreso'] = pd.to_datetime(df['FECHA DE INGRESO (AAAAMMDD)'], errors='coerce')
        
        if 'FECHA DE RETIRO (AAAAMMDD)' in df.columns:
            df['fecha_retiro'] = pd.to_datetime(df['FECHA DE RETIRO (AAAAMMDD)'], errors='coerce')
        
        # Mapear columnas específicas a nombres estandarizados
        if 'EMPRESA' in df.columns:
            df['empresa'] = df['EMPRESA']
        
        if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in df.columns:
            df['tipo_novedad'] = df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        
        if 'TIPO DE CONTRATO' in df.columns:
            df['tipo_contrato'] = df['TIPO DE CONTRATO']
        if 'AREA' in df.columns:
            df['area'] = df['AREA']
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
        
        # CAMBIO IMPORTANTE: Eliminar filas que estén completamente vacías
        # Primero, rellenar valores vacíos con NaN
        df = df.replace('', pd.NA)
        
        # Eliminar filas donde todas las columnas son NaN
        df = df.dropna(how='all')
        
        # Procesamiento de datos (convertir fechas, etc.)
        if 'FECHA DE INGRESO (AAAAMMDD)' in df.columns:
            df['fecha_ingreso'] = pd.to_datetime(df['FECHA DE INGRESO (AAAAMMDD)'], errors='coerce')
        
        if 'FECHA DE RETIRO (AAAAMMDD)' in df.columns:
            df['fecha_retiro'] = pd.to_datetime(df['FECHA DE RETIRO (AAAAMMDD)'], errors='coerce')
        
        # Mapear columnas específicas a nombres estandarizados
        if 'PROGRAMA AL QUE PERTENECE' in df.columns:
            df['programa'] = df['PROGRAMA AL QUE PERTENECE']
        
        if 'TIPO DE NOVEDAD (ACTIVO/RETIRADO)' in df.columns:
            df['tipo_novedad'] = df['TIPO DE NOVEDAD (ACTIVO/RETIRADO)']
        
        if 'TIPO DE CONTRATO' in df.columns:
            df['tipo_contrato'] = df['TIPO DE CONTRATO']
        
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
        range_name = 'Aprendices!A1:AN1000'  # Extendido para incluir la columna AN
        
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
        
        # Procesamiento de datos (convertir fechas, etc.)
        if 'FECHA DE INGRESO' in df.columns:
            df['fecha_ingreso'] = pd.to_datetime(df['FECHA DE INGRESO'], errors='coerce')
        
        if 'FECHA RETIRO' in df.columns:
            df['fecha_retiro'] = pd.to_datetime(df['FECHA RETIRO'], errors='coerce')
        
        # Mapear columnas específicas a nombres estandarizados
        if 'AREA' in df.columns:
            df['area'] = df['AREA']
        
        if 'TIPO DE NOVEDAD' in df.columns:
            df['tipo_novedad'] = df['TIPO DE NOVEDAD']
        
        if 'TIPO DE CONTRATO' in df.columns:
            df['tipo_contrato'] = df['TIPO DE CONTRATO']
        
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

# Función para cargar todos los datos
def load_all_data():
    """
    Carga los datos de todas las hojas y los retorna como un diccionario de DataFrames.
    """
    planta_df = load_planta_data()
    manipuladoras_df = load_manipuladoras_data()
    aprendices_df = load_aprendices_data()
       
    return {
        'planta': planta_df,
        'manipuladoras': manipuladoras_df,
        'aprendices': aprendices_df
    }

# Función para guardar copias de seguridad de los datos
def save_backup_data():
    """
    Guarda copias de seguridad de los datos en archivos CSV locales.
    """
    try:
        # Crear directorio si no existe
        os.makedirs('data_backup', exist_ok=True)
        
        # Cargar datos
        data_dict = load_all_data()
        
        # Guardar cada DataFrame como CSV
        for name, df in data_dict.items():
            if not df.empty:
                df.to_csv(f'data_backup/{name}_backup.csv', index=False)
        
        st.success("Copias de seguridad guardadas correctamente")
    except Exception as e:
        st.error(f"Error al guardar copias de seguridad: {e}")

# Función para formatear fechas
def format_date(date):
    """
    Formatea una fecha como string en formato DD/MM/YYYY.
    """
    if pd.isna(date):
        return ""
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except:
            return date
    return date.strftime('%d/%m/%Y')

# Función para filtrar datos por rango de fechas
def filter_by_date_range(df, start_date, end_date, date_column='fecha_ingreso'):
    """
    Filtra un DataFrame por un rango de fechas.
    
    Args:
        df: DataFrame de pandas
        start_date: Fecha de inicio (inclusive)
        end_date: Fecha de fin (inclusive)
        date_column: Nombre de la columna de fecha
        
    Returns:
        DataFrame filtrado
    """
    if df.empty or date_column not in df.columns:
        return df
    
    # Asegurar que la columna de fecha es datetime
    if not pd.api.types.is_datetime64_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    
    # Filtrar por rango de fechas
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df[mask]

# Función para limpiar la caché de Streamlit
def clear_cache():
    """
    Limpia la caché de datos de Streamlit.
    """
    st.cache_data.clear()
    st.success("Caché limpiada correctamente")