import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Importar únicamente el nuevo módulo de indicadores
import indicadores

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Indicadores de Contratación",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones de utilidad
def add_logo():
    """Agrega un logo o título estilizado al sidebar"""
    st.sidebar.markdown("""
    <div style='text-align: center'>
        <h1 style='color: #4682B4'>📊 Dashboard</h1>
        <h2 style='color: #5F9EA0'>Indicadores de Contratación</h2>
    </div>
    """, unsafe_allow_html=True)

def show_info():
    """Muestra información sobre el dashboard"""
    st.sidebar.markdown("---")
    
    # Mostrar solo la hora actual
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.sidebar.markdown(f"**Última actualización:** {now}")

# Función principal
def main():
    """Función principal que ejecuta la aplicación"""
    # Agregar logo y menú de navegación
    add_logo()
    
    # Menú de navegación simplificado
    menu = st.sidebar.radio(
        "Navegación",
        ["🏠 Inicio", "📊 Indicadores de Contrato"]
    )
    
    # Mostrar información en el sidebar
    show_info()
    
    # Renderizar la sección seleccionada
    if menu == "🏠 Inicio":
        show_home()
    elif menu == "📊 Indicadores de Contrato":
        indicadores.run()

def show_home():
    """Muestra la página de inicio"""
    st.title("Dashboard de Indicadores de Contratación")
    
    st.markdown("""
    ## Bienvenido al Dashboard de Indicadores de Contratación
    
    Este dashboard simplificado permite visualizar:
    
    * **Total de tipos de contratos** combinando datos de Manipuladoras y Planta
    
    ### 📊 Características
    
    - Visualización de datos combinados en una tabla simple
    - Conteo total por cada tipo de contrato
    
    ### 🚀 Comenzar
    
    Utilice el menú de navegación en la barra lateral para explorar el dashboard.
    """)
    
    # Mostrar card con enlace a la sección
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
        <h3>📊 Indicadores de Contrato</h3>
        <p>Análisis de tipos de contrato por fuente</p>
        <br/>
    </div>
    """, unsafe_allow_html=True)
    
    # Agregar información de datos
    st.subheader("Información de los Datos")
    st.markdown("""
    * **Manipuladoras**: Columna "TIPO DE CONTRATO" (Posición T)
    * **Planta**: Columna "TIPO DE CONTRATO" (Posición M)
    """)

if __name__ == "__main__":
    main()