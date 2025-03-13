import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Importar los módulos de visualización
import Contratos
import Novedades
import Empresas
import motivo  # Nuevo módulo de motivos de retiro

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
    
    # Menú de navegación
    menu = st.sidebar.radio(
        "Navegación",
        ["🏠 Inicio", "📑 Contratos", "🔄 Novedades", "🏢 Empresas", "🚪 Motivos de Retiro"]  # Añadido nuevo ítem
    )
    
    # Mostrar información en el sidebar
    show_info()
    
    # Renderizar la sección seleccionada
    if menu == "🏠 Inicio":
        show_home()
    elif menu == "📑 Contratos":
        Contratos.run()
    elif menu == "🔄 Novedades":
        Novedades.run()
    elif menu == "🏢 Empresas":
        Empresas.run()
    elif menu == "🚪 Motivos de Retiro":  # Nueva sección
        motivo.run()

def show_home():
    """Muestra la página de inicio"""
    st.title("Dashboard de Indicadores de Contratación")
    
    st.markdown("""
    ## Bienvenido al Dashboard de Indicadores de Contratación
    
    Este dashboard permite visualizar y analizar indicadores relacionados con:
    
    * **Tipos de contratos** por fuente de datos
    * **Estados de contratación** (tipos de novedad)
    * **Distribución por empresas, programas y áreas**
    * **Motivos de retiro** del personal  # Nueva funcionalidad
    
    ### 📊 Características
    
    - Visualización de datos de tres fuentes: Manipuladoras, Planta y Aprendices
    - Gráficos interactivos
    - Análisis comparativo
    - Exportación de datos
    
    ### 🚀 Comenzar
    
    Utilice el menú de navegación en la barra lateral para explorar las diferentes secciones del dashboard.
    """)
    
    # Mostrar cards con enlaces a las diferentes secciones
    col1, col2, col3, col4 = st.columns(4)  # Ahora 4 columnas para incluir la nueva sección
    
    with col1:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h3>📑 Contratos</h3>
            <p>Análisis de tipos de contrato por fuente</p>
            <br/>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h3>🔄 Novedades</h3>
            <p>Análisis de estados de contratación</p>
            <br/>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h3>🏢 Empresas</h3>
            <p>Distribución por empresas, programas y áreas</p>
            <br/>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h3>🚪 Motivos de Retiro</h3>
            <p>Análisis de causas de retiro de personal</p>
            <br/>
        </div>
        """, unsafe_allow_html=True)
    
    # Agregar información de datos
    st.subheader("Información de los Datos")
    st.markdown("""
       
    * **Manipuladoras**: Contiene información sobre programas, tipo de novedad, fechas, tipos de contrato y motivos de retiro.
    * **Planta**: Contiene información sobre empresas, fechas, tipo de novedad, tipos de contrato y motivos de retiro.
    * **Aprendices**: Contiene información sobre áreas, tipo de novedad, fechas y tipos de contrato.
    """)

if __name__ == "__main__":
    main()