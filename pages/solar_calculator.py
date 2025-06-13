# pages/solar_calculator.py
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from utils.pdf_report import PDFReport
import tempfile
from geopy.geocoders import Nominatim
import json
from logic.energy.consumption_calculator import ConsumptionCalculator
from logic.energy.system_calculator import SystemCalculator
from logic.financial.metrics_calculator import FinancialMetricsCalculator
from logic.generation.data_generator import DataGenerator
from logic.utils.data_loader import get_monthly_irradiance, get_price_per_kwh
from logic.utils.billing_calculator import BillingCalculator


@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

pricing_data = load_json("data/pricing.json")
irradiance_monthly = load_json("data/irradiance_monthly.json")



def geocode_address(address):
    geolocator = Nominatim(user_agent="solar-calculator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

def render():
    if "step" not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.title("Solar Energy Calculator")
        st.header("Step 1: Electricity Consumption and Tariff Info")

        with st.form("step1_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: kwh1 = st.number_input("Month 1 (kWh)", min_value=0, step=100)
            with col2: kwh2 = st.number_input("Month 2 (kWh)", min_value=0, step=100)
            with col3: kwh3 = st.number_input("Month 3 (kWh)", min_value=0, step=100)
            with col4: kwh4 = st.number_input("Month 4 (kWh)", min_value=0, step=100)

            distributor = st.selectbox("Electricity Distributor", list(pricing_data.keys()))
            tariff = st.selectbox("Tariff Type", list(pricing_data[distributor].keys()))

            if st.form_submit_button("Next"):
                st.session_state.kwh = [kwh1, kwh2, kwh3, kwh4]
                st.session_state.distributor = distributor
                st.session_state.tariff = tariff
                st.session_state.step = 2
                st.rerun()

    elif st.session_state.step == 2:
        st.title("Solar Energy Calculator")
        st.header("Step 2: Location and System Sizing Preference")

        with st.form("step2_form"):
            department = st.selectbox("Department", list(irradiance_monthly.keys()))
            sizing_pref = st.selectbox("Sizing Preference", ["Minimum", "Balanced", "Maximum"])

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.form_submit_button("Back"):
                    st.session_state.step = 1
                    st.rerun()
            with col2:
                if st.form_submit_button("Next"):
                    st.session_state.department = department
                    st.session_state.sizing_pref = sizing_pref
                    st.session_state.step = 3
                    st.rerun()

    elif st.session_state.step == 3:
        st.title("Solar Energy Calculator")
        st.header("Step 3: Personal Information")

        with st.form("step3_form"):
          st.subheader("Contact and Location Information")

          col1, col2 = st.columns(2)
          with col1:
              first_name = st.text_input("First Name", max_chars=50)
              email = st.text_input("Email")
              phone = st.text_input("Phone")

          with col2:
              last_name = st.text_input("Last Name", max_chars=50)
              address = st.text_input("Address")
              latitude = st.number_input("Latitude", format="%.6f")
              longitude = st.number_input("Longitude", format="%.6f")

          col3, col4 = st.columns([1, 3])
          with col3:
              if st.form_submit_button("Back"):
                  st.session_state.step = 2
                  st.rerun()
          with col4:
              if st.form_submit_button("Continue"):
                  st.session_state.personal_info = {
                      "first_name": first_name,
                      "last_name": last_name,
                      "email": email,
                      "phone": phone,
                      "address": address,
                      "latitude": latitude,
                      "longitude": longitude,
                  }
                  st.session_state.step = 4
                  st.rerun()


    elif st.session_state.step == 4:
        st.title("Solar Energy Calculator")
        st.success("Calculation Complete")

        # Load session values
        kwh_list = st.session_state.kwh
        distributor = st.session_state.distributor
        rate_type = st.session_state.tariff
        dept = st.session_state.department
        pref = st.session_state.sizing_pref

        # --- Energy Calculations ---
        avg_kwh = ConsumptionCalculator.calculate_average_monthly_consumption(kwh_list)
        annual_kwh = ConsumptionCalculator.calculate_annual_consumption(avg_kwh)
        monthly_kwh_sim = DataGenerator.simulate_monthly_distribution(annual_kwh)
        monthly_irradiance = irradiance_monthly[dept]
        annual_irradiance = sum(monthly_irradiance) / 12

        system_kw = SystemCalculator.calculate_required_system_size_kw(avg_kwh, annual_irradiance)
        if pref.lower() == "minimum":
            system_kw *= 0.8
        elif pref.lower() == "maximum":
            system_kw *= 1.2

        panels = SystemCalculator.calculate_number_of_panels(system_kw)
        installed_kw = SystemCalculator.calculate_installed_power_kw(panels)
        area = SystemCalculator.calculate_required_area_m2(panels)
        annual_gen = SystemCalculator.calculate_annual_generation_kwh(panels, annual_irradiance)
        coverage = SystemCalculator.calculate_coverage_percentage(annual_gen, avg_kwh, pref)
        monthly_generation = DataGenerator.simulate_monthly_generation_from_irradiance(panels, monthly_irradiance)

        # --- Financial ---
        financial = BillingCalculator.generate_annual_cost_comparison(
            monthly_kwh_sim, monthly_generation, distributor, rate_type, dept
        )

        investment = FinancialMetricsCalculator.calculate_investment_cost(installed_kw)
        payback = FinancialMetricsCalculator.calculate_payback_period(investment, financial["annual_savings"])
        roi = FinancialMetricsCalculator.calculate_roi(investment, financial["annual_savings"])
        irr = FinancialMetricsCalculator.calculate_irr(
            FinancialMetricsCalculator.calculate_cashflow_list(investment, financial["annual_savings"])
        )
        co2 = FinancialMetricsCalculator.calculate_co2_saved(annual_gen)
        trees = FinancialMetricsCalculator.calculate_tree_equivalents(co2)

        # --- Output UI ---
        # Personal Info Header Section
        personal_info = st.session_state.get("personal_info", {})

        st.markdown("### 🔎 User Summary")

        st.markdown(
            f"""
            <div style="border:1px solid #DDD;padding:1rem;border-radius:6px;margin-bottom:1rem;">
                <b>Name:</b> {personal_info.get('first_name', '')} {personal_info.get('last_name', '')} &nbsp;&nbsp;
                <b>Email:</b> {personal_info.get('email', '')} &nbsp;&nbsp;
                <b>Phone:</b> {personal_info.get('phone', '')}<br>
                <b>Address:</b> {personal_info.get('address', '')}<br>
                <b>Coordinates:</b> Lat {personal_info.get('latitude', '')}, Lon {personal_info.get('longitude', '')}
            </div>
            """,
            unsafe_allow_html=True
        )

        tab1, tab2, tab3 = st.tabs(["📋 Numeric Results", "📈 Graphs", "🗺️ Map"])


        with tab1:
            st.subheader("Energy Results")
            st.write(f"• Avg Monthly Consumption (kWh): **{avg_kwh}**")
            st.write(f"• Annual Consumption (kWh): **{annual_kwh}**")
            st.write(f"• System Size (kW): **{round(system_kw, 2)}**")
            st.write(f"• Number of Panels: **{panels}**")
            st.write(f"• Required Area (m²): **{area}**")
            st.write(f"• Annual Generation (kWh): **{annual_gen}**")
            st.write(f"• Coverage (%): **{coverage}%**")

            st.divider()
            st.subheader("Financial & Environmental Results")
            st.write(f"• Investment Cost (Q): **Q{investment}**")
            st.write(f"• Annual Savings (Q): **Q{financial['annual_savings']}**")
            st.write(f"• Payback Period (years): **{payback}**")
            st.write(f"• ROI (%): **{roi}**")
            st.write(f"• IRR (%): **{irr}**")
            st.write(f"• CO₂ Saved (kg/year): **{co2}**")
            st.write(f"• Tree Equivalents: **{trees}**")

        with tab2:
        
            st.info("Graphs will be added in the next step.")
            
            # Generation vs. Consumption
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            
            chart_data = pd.DataFrame({
              "Month": months,
              "Consumption (kWh)": monthly_kwh_sim,
              "Generation (kWh)": monthly_generation
            })

            chart_data.set_index("Month", inplace=True)

            st.bar_chart(chart_data, stack=False, color=["#0B284C", "#FFBF41"])
            
            # Cumulative cash flow data
            # Using simple st
            # Create DataFrame
            # cashflow_df = pd.DataFrame({
            #     "Year": years,
            #     "Cumulative Cashflow (Q)": cumulative
            # })
            # cashflow_df.set_index("Year", inplace=True)

            # st.subheader("Cumulative Cash Flow Over Time")
            # st.bar_chart(cashflow_df)
            import plotly.graph_objects as go

            # Changing color
            cashflow = FinancialMetricsCalculator.calculate_cashflow_list(investment, financial["annual_savings"])
            years = list(range(len(cashflow)))
            cumulative = [sum(cashflow[:i+1]) for i in range(len(cashflow))]

            colors = ["lightcoral" if val < 0 else "lightgreen" for val in cumulative]

            fig = go.Figure(data=[
                go.Bar(
                    x=years,
                    y=cumulative,
                    marker_color=colors
                )
            ])

            fig.update_layout(
                title="Cumulative Cash Flow Over Time",
                xaxis_title="Year",
                yaxis_title="Cumulative Value (Q)",
                showlegend=False,
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)
            
            # Simulate 25 years of consumption and generation
            # Simulate annual data series for 25 years
            years = list(range(1, 31))
            annual_gen_series = DataGenerator.simulate_annual_generation_with_degradation(annual_gen, years=30)
            annual_cons_series = DataGenerator.simulate_annual_data_series(annual_kwh, years=30, variation=0.04)

            # Create the line chart
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=years,
                y=annual_cons_series,
                mode='lines+markers',
                name='Consumption (kWh)',
                line=dict(color='steelblue')
            ))

            fig.add_trace(go.Scatter(
                x=years,
                y=annual_gen_series,
                mode='lines+markers',
                name='Generation (kWh)',
                line=dict(color='orange')
            ))

            fig.update_layout(
                title="Annual Solar Generation vs Consumption Over 25 Years",
                xaxis_title="Year",
                yaxis_title="Energy (kWh)",
                height=400,
                margin=dict(t=50, b=40),
                legend=dict(x=0.01, y=0.99)
            )

            st.subheader("Annual Solar Generation vs Consumption")
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly irradiance chart for the selected department
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            fig = go.Figure(data=[
                go.Bar(x=months, y=monthly_irradiance, marker_color="#FFBF41")
            ])

            fig.update_layout(
                title=f"Monthly Irradiance in {dept}",
                xaxis_title="Month",
                yaxis_title="Irradiance (kWh/m²/day)",
                height=400,
                showlegend=False
            )

            st.subheader("Monthly Solar Irradiance")
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
          st.subheader("System Location")
      
          personal_info = st.session_state.get("personal_info", {})
          lat = personal_info.get("latitude")
          lon = personal_info.get("longitude")
      
          if lat and lon:
              st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
          else:
              st.info("Coordinates not available. Please provide them in Step 3.")









