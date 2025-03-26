import streamlit as st
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
        ["📊 Indicadores de Contrato"]
    )
    
    # Mostrar información en el sidebar
    show_info()
    
    # Mostrar solo el módulo de indicadores
    indicadores.run()

if __name__ == "__main__":
    main()