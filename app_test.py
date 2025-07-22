import streamlit as st

# Page configuration
st.set_page_config(page_title="Siempre Energy App", layout="wide")

# Sidebar navigation
st.sidebar.title("📋 Menú")
section = st.sidebar.radio("Navegar", ["🏠 Home", "🔆 Solar Calculator", "📊 Dashboard AMM", "📡 Dashboard CNEE"])

# Page: Home
if section == "🏠 Home":
    st.title("Bienvenido a Siempre Energy")
    st.markdown("""
        Usa el menú de la izquierda para acceder a las diferentes funciones disponibles.
        
        - **Solar Calculator**: Calcula el tamaño óptimo del sistema solar, ahorro económico y métricas ambientales.
        - **Dashboard AMM**: Visualiza los datos de generación energética desde AMM Guatemala.

        Más funciones estarán disponibles pronto.
    """)

# Page: Solar Calculator
elif section == "🔆 Solar Calculator":
    from pages import solar_calculator
    solar_calculator.render()

# Page: Dashboard AMM
elif section == "📊 Dashboard AMM":
    from pages import amm_dash
    amm_dash.render()

# Page: Dashboard AMM
elif section == "📡 Dashboard CNEE":
    from pages import cnee_dash
    cnee_dash.render()