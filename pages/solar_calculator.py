# pages/solar_calculator.py

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import tempfile
import json

from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from logic.utils.pdf_report import PDFReport
from io import BytesIO
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


def render():
    if "step" not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.title("Solar Energy Calculator")
        st.header("Step 1: Electricity Consumption and Tariff Info")
        st.text("Please select EGGSA and BT for correct results. Other optionas are still WIP.")

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
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", max_chars=50)
                last_name = st.text_input("Last Name", max_chars=50)
            with col2:
                email = st.text_input("Email")
                phone = st.text_input("Phone")

            col3, col4 = st.columns([1, 3])
            with col3:
                if st.form_submit_button("Back"):
                    st.session_state.step = 2
                    st.rerun()
            with col4:
                if st.form_submit_button("Next"):
                    st.session_state.personal_info = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                    }
                    st.session_state.step = 4
                    st.rerun()

    elif st.session_state.step == 4:
        st.title("Solar Energy Calculator")
        st.header("Step 4: System Location")
        st.text("Enter address by name or by coordinates. If the pin is not set exactly after entering the address you can click on the position desired.")

        DEFAULT_LAT = 14.6349
        DEFAULT_LON = -90.5069

        if "pin_lat" not in st.session_state:
            st.session_state.pin_lat = DEFAULT_LAT
        if "pin_lon" not in st.session_state:
            st.session_state.pin_lon = DEFAULT_LON

        # Address and manual input section (separate form for search)
        with st.form("search_form"):
            address = st.text_input("Enter Address e.g. (19 Calle 16-29, Zona 7, Mixco, Guatemala)", value=st.session_state.get("location_info", {}).get("address", ""))
            col1, col2 = st.columns(2)
            with col1:
                manual_lat = st.text_input("Latitude (optional instead of address)")
            with col2:
                manual_lon = st.text_input("Longitude (optional instead of address)")

            search_clicked = st.form_submit_button("Search Location")

            if search_clicked:
                if manual_lat and manual_lon:
                    try:
                        st.session_state.pin_lat = float(manual_lat)
                        st.session_state.pin_lon = float(manual_lon)
                        st.success("📍 Coordinates set from manual input.")
                    except ValueError:
                        st.warning("Invalid latitude or longitude values.")
                elif address:
                    geolocator = Nominatim(user_agent="solar-calculator")
                    try:
                        location = geolocator.geocode(address, timeout=10)
                        if location:
                            st.session_state.pin_lat = location.latitude
                            st.session_state.pin_lon = location.longitude
                            st.success("📍 Coordinates set from address.")
                        else:
                            st.warning("Address not found.")
                    except (GeocoderTimedOut, GeocoderUnavailable) as e:
                        st.error(f"Geocoding error: {e}")
        
        st.text("If entered address by name and it didnt work try beeing as close as the example address.")

        # Show map
        lat = st.session_state.pin_lat
        lon = st.session_state.pin_lon

        m = folium.Map(
            location=[lat, lon],
            zoom_start=15,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri Satellite"
        )
        folium.Marker([lat, lon], popup="Selected Location").add_to(m)
        m.add_child(folium.LatLngPopup())
        map_data = st_folium(m, width=700, height=500)

        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.pin_lat = clicked["lat"]
            st.session_state.pin_lon = clicked["lng"]
            st.success(f"📍 Pin updated via map click: ({clicked['lat']}, {clicked['lng']})")

        st.markdown(f"**Current Coordinates:** `{st.session_state.pin_lat}`, `{st.session_state.pin_lon}`")

        # Navigation form
        with st.form("nav_buttons_form"):
            col3, col4 = st.columns([1, 3])
            with col3:
                back = st.form_submit_button("Back")
            with col4:
                continue_btn = st.form_submit_button("Continue")

            if back:
                st.session_state.step = 3
                st.rerun()
            if continue_btn:
                # Update location_info for map tab
                st.session_state.location_info = {
                    "address": address,
                    "latitude": st.session_state.pin_lat,
                    "longitude": st.session_state.pin_lon,
                }

                # Add location to personal_info summary as well
                if "personal_info" not in st.session_state:
                    st.session_state.personal_info = {}

                st.session_state.personal_info.update({
                    "address": address,
                    "latitude": st.session_state.pin_lat,
                    "longitude": st.session_state.pin_lon,
                })
                st.session_state.step = 5
                st.rerun()
                


    elif st.session_state.step == 5:
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
    
        # --- Store Results Once ---
        if "results" not in st.session_state:
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
    
            st.session_state.results = {
                "financial": financial,
                "investment": investment,
                "payback": payback,
                "roi": roi,
                "irr": irr,
                "co2": co2,
                "trees": trees
            }
    
        # Retrieve stored values
        financial = st.session_state.results["financial"]
        investment = st.session_state.results["investment"]
        payback = st.session_state.results["payback"]
        roi = st.session_state.results["roi"]
        irr = st.session_state.results["irr"]
        co2 = st.session_state.results["co2"]
        trees = st.session_state.results["trees"]
    
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
            st.write(f"• CO2 Saved (kg/year): **{co2}**")
            st.write(f"• Tree Equivalents: **{trees}**")
            st.divider()
            # --- Download PDF Report ---
            if st.button("📄 PDF Report"):
                pdf = PDFReport()
                pdf.add_cover_page()
                pdf.add_page()
                pdf.add_user_info(st.session_state.personal_info)
            
                energy_output = {
                    "Average Monthly Consumption (kWh)": avg_kwh,
                    "Annual Consumption (kWh)": annual_kwh,
                    "System Size (kW)": round(system_kw, 2),
                    "Number of Panels": panels,
                    "Required Area (m²)": area,
                    "Annual Generation (kWh)": annual_gen,
                    "Coverage (%)": coverage
                }
            
                financial_output = {
                    "Investment Cost (Q)": investment,
                    "Annual Savings (Q)": financial["annual_savings"],
                    "Payback Period (years)": payback,
                    "ROI (%)": roi,
                    "IRR (%)": irr,
                    "CO2 Saved (kg/year)": co2,
                    "Tree Equivalents": trees,
                    "Annual Cost Without Solar (Q)": financial["annual_cost_without_solar"],
                    "Annual Cost With Solar (Q)": financial["annual_cost_with_solar"]
                }
            
                pdf.add_results(energy_output, financial_output)                
            
                buffer = pdf.save_to_buffer()
            
                st.download_button(
                    label="📥 Click to Download PDF",
                    data=buffer,
                    file_name="solar_report.pdf",
                    mime="application/pdf"
                )



        with tab2:
        
            st.info("Graphs will be added in the next step.")
            
            # Month ordering
            months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            # Create DataFrame
            chart_data = pd.DataFrame({
                "Month": months_order,
                "Consumption (kWh)": monthly_kwh_sim,
                "Generation (kWh)": monthly_generation
            })

            # Sort Month column to enforce correct order
            chart_data["Month"] = pd.Categorical(chart_data["Month"], categories=months_order, ordered=True)
            chart_data.sort_values("Month", inplace=True)

            # Create the bar chart
            fig = go.Figure(data=[
                go.Bar(name="Consumption (kWh)", x=chart_data["Month"], y=chart_data["Consumption (kWh)"], marker_color="#0B284C"),
                go.Bar(name="Generation (kWh)", x=chart_data["Month"], y=chart_data["Generation (kWh)"], marker_color="#FFBF41")
            ])

            # Customize layout
            fig.update_layout(
                barmode="group",
                title="Monthly Energy Consumption vs Generation",
                xaxis_title="Month",
                yaxis_title="Energy (kWh)",
                height=400,
                margin=dict(t=50, b=40),
                legend=dict(x=0.01, y=0.99)
            )

            # Show in Streamlit
            st.plotly_chart(fig, use_container_width=True)
            
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

            st.plotly_chart(fig, use_container_width=True)
        
        # Inside tab3:
        with tab3:
            st.subheader("System Location")

            # Try location_info first
            location_info = st.session_state.get("location_info", {})

            # Use session state pin as fallback
            lat = location_info.get("latitude", st.session_state.get("pin_lat"))
            lon = location_info.get("longitude", st.session_state.get("pin_lon"))
            address = location_info.get("address", st.session_state.get("address", ""))

            if lat and lon:
                st.write(f"📍 **Coordinates:** `{lat}`, `{lon}`")
                if address:
                    st.write(f"🏠 **Address:** {address}")

                m = folium.Map(
                    location=[lat, lon],
                    zoom_start=15,
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri Satellite"
                )
                folium.Marker([lat, lon], popup="System Location").add_to(m)
                st_folium(m, width=700, height=500)
            else:
                st.info("📌 Location not set. Please return to Step 4.")







