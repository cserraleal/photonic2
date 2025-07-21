# app.py

import streamlit as st

# Step 1: Load users from secrets
USERS = st.secrets["users"]

# Step 2: Page configuration
st.set_page_config(page_title="Siempre Energy App", layout="wide")

# Step 3: Login mechanism
def login_screen():
    st.title("🔒 Login Required")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bienvenido {username}")
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

def logout_button():
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# Step 4: Authentication state check
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Step 5: Render app or login
if st.session_state.logged_in:
    # Sidebar menu
    st.sidebar.title("📋 Menu")
    st.sidebar.markdown(f"👤 Usuario: `{st.session_state.username}`")
    logout_button()
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
        from pages import solar_calculator
        solar_calculator.render()

else:
    login_screen()

