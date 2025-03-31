import streamlit as st
from datetime import datetime

# Importar los módulos necesarios
import indicadores
import areas_contratos
import personal_activo
import retiros  # Nuevo módulo de retiros

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
    
    # Menú de navegación con todos los módulos
    menu = st.sidebar.radio(
        "Navegación",
        ["📊 Indicadores de Contrato", "📋 Áreas por Tipo de Contrato", "👥 Personal Activo", "🚪 Motivos de Retiro"]
    )
    
    # Mostrar información en el sidebar
    show_info()
    
    # Mostrar el módulo seleccionado
    if menu == "📊 Indicadores de Contrato":
        indicadores.run()
    elif menu == "📋 Áreas por Tipo de Contrato":
        areas_contratos.run()
    elif menu == "👥 Personal Activo":
        personal_activo.run()
    else:
        retiros.run()

if __name__ == "__main__":
    main()