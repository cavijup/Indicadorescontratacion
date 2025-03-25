import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import os

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

# Función para cargar todos los datos
def load_all_data():
    """
    Carga los datos de las hojas Planta y Manipuladoras y los retorna como un diccionario de DataFrames.
    """
    planta_df = load_planta_data()
    manipuladoras_df = load_manipuladoras_data()
    
    return {
        'planta': planta_df,
        'manipuladoras': manipuladoras_df
    }

# Función para limpiar la caché de Streamlit
def clear_cache():
    """
    Limpia la caché de datos de Streamlit.
    """
    st.cache_data.clear()
    st.success("Caché limpiada correctamente")