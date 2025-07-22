# app.py

import streamlit as st

# Set page configuration
st.set_page_config(page_title="Siempre Energy App", layout="wide")

# Sidebar menu
st.sidebar.title("📋 Menu")
section = st.sidebar.radio("Navigate", ["🏠 Home", "🔆 Solar Calculator"])

# Page: Home
if section == "🏠 Home":
    st.title("Bienvenido a Siempre Energy")
    st.markdown("""
        Usa el menú de la izquierda para acceder a las diferentes funciones disponibles.
        
        - **Solar Calculator**: Calcula el tamaño óptimo del sistema solar, ahorro económico y métricas ambientales.
        
        Más funciones estarán disponibles pronto.
    """)

# Page: Solar Calculator
elif section == "🔆 Solar Calculator":
    from photonic.pages import solar_calculator
    solar_calculator.render()
