# pages/amm_dash.py

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date

def render():
    URLS = {
        "Tecnología": "https://wl12.amm.org.gt/GraficaPW/graficaAreaScada?dt=",
        "Tipo de Recurso": "https://wl12.amm.org.gt/GraficaPW/graficaTipoRecurso?dt=",
        "Tipo de Combustible": "https://wl12.amm.org.gt/GraficaPW/graficaCombustible?dt="
    }

    st.title("Dashboard de Generación Energética - Guatemala")

    opcion = st.selectbox("Selecciona categoría de datos:", list(URLS.keys()))
    fecha = st.date_input("Selecciona una fecha:", value=date.today(), format="DD/MM/YYYY")
    fecha_str = fecha.strftime("%d/%m/%Y")

    url = URLS[opcion] + fecha_str
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        st.error("Error al obtener los datos desde AMM.")
        st.stop()

    df = pd.DataFrame(data)
    df["hora"] = pd.to_numeric(df["hora"], errors="coerce")
    df = df.dropna(subset=["hora"])

    # Split data into "DEMANDA LOCAL PROG" and the rest
    df_demanda = df[df["tipo"] == "DEMANDA LOCAL PROG"]
    df_otros = df[df["tipo"] != "DEMANDA LOCAL PROG"]

    fig = go.Figure()

    # Add area charts (stacked)
    for tipo in df_otros["tipo"].unique():
        sub_df = df_otros[df_otros["tipo"] == tipo]
        fig.add_trace(go.Scatter(
            x=sub_df["hora"],
            y=sub_df["potencia"],
            mode="lines",
            stackgroup="uno",  # Enables area stacking
            name=tipo
        ))

    # Add line for DEMANDA LOCAL PROG
    if not df_demanda.empty:
        fig.add_trace(go.Scatter(
            x=df_demanda["hora"],
            y=df_demanda["potencia"],
            mode="lines",
            name="DEMANDA LOCAL PROG",
            line=dict(color="red", width=3, dash="dash")
        ))

    fig.update_layout(
        title=f"Generación y Demanda ({opcion}) - {fecha_str}",
        xaxis_title="Hora",
        yaxis_title="Potencia (MW)",
        hovermode="x unified",
        legend_title="Tipo"
    )

    st.plotly_chart(fig, use_container_width=True)

