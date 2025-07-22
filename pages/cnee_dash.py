# pages/cnee_dash.py

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

def render():
    st.title("📡 CNEE Dashboard")
    st.markdown("Visualización de tarifas históricas e integración de costos.")

    # Mapping of distribuidoras
    DISTRIBUIDORAS = {
        "EEGSA": 1,
        "ENERSA": 2,
        "DEE": 3,
        "EMRE": 4,
        "EMSA": 5,
        "ENERGIA Y DESARROLLO": 6,
        "EEG": 7,
        "EMMEGUA": 8,
        "EMMGUALAN": 9,
        "EMSAZACAPA": 10,
        "EMCOGUA": 11,
        "EMCOATEPEQUE": 12
    }

    # Dropdown
    selected_dist = st.selectbox("Selecciona la distribuidora", options=DISTRIBUIDORAS.keys())
    dist_id = DISTRIBUIDORAS[selected_dist]

    # --- Graph 1: BTS vs TS histórico ---
    try:
        url_1 = f"https://www.cnee.gob.gt/Calculadora/datos/db.BTS_TS.php?distribuidora={dist_id}"
        data_1 = requests.get(url_1).json()
        df_1 = pd.DataFrame(data_1)

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_1["category"], y=df_1["value1"], mode="lines+markers", name="Tarifa TS"))
        fig1.add_trace(go.Scatter(x=df_1["category"], y=df_1["value2"], mode="lines+markers", name="Tarifa BTS"))
        fig1.update_layout(
            title="Histórico de Tarifa BTS vs TS",
            xaxis_title="Fecha",
            yaxis_title="Tarifa (Q/kWh)",
            legend_title="Tarifa",
        )
        st.plotly_chart(fig1, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar la gráfica 1: {e}")

    # --- Graph 2: Integración de Costos BTS ---
    try:
        url_2 = f"https://www.cnee.gob.gt/Calculadora/datos/db.BTS.php?distribuidora={dist_id}"
        data_2 = requests.get(url_2).json()
        df_2 = pd.DataFrame(data_2)
        df_2["Generacion"] = df_2["Generacion"].astype(float)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_2["hasta"], y=df_2["Generacion"], name="Generación"))
        fig2.add_trace(go.Bar(x=df_2["hasta"], y=df_2["Distribucion"], name="Distribución"))
        fig2.add_trace(go.Bar(x=df_2["hasta"], y=df_2["Transporte"], name="Transporte"))
        fig2.add_trace(go.Bar(x=df_2["hasta"], y=df_2["Perdidas"], name="Pérdidas"))
        fig2.update_layout(
            title="Integración de Costos – Tarifa BTS",
            xaxis_title="Fecha",
            yaxis_title="Costo (Q/kWh)",
            legend_title="Componente",
            barmode="stack",
            yaxis=dict(range=[0, 2])
        )
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar la gráfica 2: {e}")


    # --- Graph 3: Integración de Costos TS (Stacked Bar) ---
    try:
        url_3 = f"https://www.cnee.gob.gt/Calculadora/datos/db.TS.php?distribuidora={dist_id}"
        data_3 = requests.get(url_3).json()
        df_3 = pd.DataFrame(data_3)
        df_3["Generación"] = df_3["Generación"].astype(float)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_3["hasta"], y=df_3["Generación"], name="Generación"))
        fig3.add_trace(go.Bar(x=df_3["hasta"], y=df_3["Distribución"], name="Distribución"))
        fig3.add_trace(go.Bar(x=df_3["hasta"], y=df_3["Transporte"], name="Transporte"))
        fig3.add_trace(go.Bar(x=df_3["hasta"], y=df_3["Pérdidas"], name="Pérdidas"))
        fig3.update_layout(
            title="Integración de Costos – Tarifa TS",
            xaxis_title="Fecha",
            yaxis_title="Costo (Q/kWh)",
            legend_title="Componente",
            barmode="stack",
            yaxis=dict(range=[0, 2])
        )
        st.plotly_chart(fig3, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar la gráfica 3: {e}")
