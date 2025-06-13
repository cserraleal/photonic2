import streamlit as st
st.set_page_config(page_title="Solar Calculator", layout="wide")

import json
from streamlit import rerun  # ✅ NEW for recent Streamlit
from logic.energy import EnergyCalculator
from logic.financial import FinancialCalculator

# ----------------------------
# Load JSON data (cached)
# ----------------------------

@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

pricing_data = load_json("data/pricing.json")
irradiance_data = load_json("data/irradiance.json")

# ----------------------------
# Initialize Step State
# ----------------------------

if "step" not in st.session_state:
    st.session_state.step = 1

# ----------------------------
# Step 1: Electricity Data
# ----------------------------

if st.session_state.step == 1:
    st.title("Solar Energy Calculator")
    st.header("Step 1: Electricity Bill and Tariff Info")

    with st.form("step1_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: mes1 = st.number_input("Month 1 (Q)", min_value=0.0, step=10.0)
        with col2: mes2 = st.number_input("Month 2 (Q)", min_value=0.0, step=10.0)
        with col3: mes3 = st.number_input("Month 3 (Q)", min_value=0.0, step=10.0)
        with col4: mes4 = st.number_input("Month 4 (Q)", min_value=0.0, step=10.0)

        distributor = st.selectbox("Electricity Distributor", list(pricing_data.keys()))
        tariff = st.selectbox("Tariff Type", list(pricing_data[distributor].keys()))

        if st.form_submit_button("Next"):
            st.session_state.bills = [mes1, mes2, mes3, mes4]
            st.session_state.distributor = distributor
            st.session_state.tariff = tariff
            st.session_state.step = 2
            rerun()

# ----------------------------
# Step 2: Location & Preference
# ----------------------------

elif st.session_state.step == 2:
    st.title("Solar Energy Calculator")
    st.header("Step 2: Location and System Sizing Preference")

    with st.form("step2_form"):
        department = st.selectbox("Department", list(irradiance_data.keys()))
        sizing_pref = st.selectbox("Sizing Preference", ["Minimum", "Balanced", "Maximum"])

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.form_submit_button("Back"):
                st.session_state.step = 1
                rerun()
        with col2:
            if st.form_submit_button("Calculate"):
                st.session_state.department = department
                st.session_state.sizing_pref = sizing_pref
                st.session_state.step = 3
                rerun()

# ----------------------------
# Step 3: Display Results
# ----------------------------

elif st.session_state.step == 3:
    st.title("Solar Energy Calculator")
    st.success("Calculation Complete")

    # Get stored values
    bills = st.session_state.bills
    distributor = st.session_state.distributor
    tariff = st.session_state.tariff
    dept = st.session_state.department
    pref = st.session_state.sizing_pref

    # Energy and Financial Calculations
    avg_kwh, annual_kwh = EnergyCalculator.calculate_consumption(bills, distributor, tariff, pricing_data)
    energy_results = EnergyCalculator.estimate_system(annual_kwh, irradiance_data, dept, pref)

    financial_results = FinancialCalculator.calculate_metrics(
        energy_results["system_kw"],
        energy_results["annual_gen_kwh"],
        avg_kwh,
        pricing_data,
        distributor,
        tariff
    )

    # Display in Tabs
    tab1, tab2 = st.tabs(["📋 Numeric Results", "📈 Graphs"])

    with tab1:
        st.subheader("Energy Results")
        st.write(f"• Avg Monthly Consumption (kWh): **{avg_kwh}**")
        st.write(f"• Annual Consumption (kWh): **{annual_kwh}**")
        st.write(f"• System Size (kW): **{energy_results['system_kw']}**")
        st.write(f"• Number of Panels: **{energy_results['panels']}**")
        st.write(f"• Required Area (m²): **{energy_results['area_m2']}**")
        st.write(f"• Annual Solar Generation (kWh): **{energy_results['annual_gen_kwh']}**")
        st.write(f"• Solar Coverage (%): **{energy_results['coverage_pct']}%**")

        st.divider()
        st.subheader("Financial & Environmental Results")
        st.write(f"• Investment Cost (Q): **Q{financial_results['investment_q']}**")
        st.write(f"• Annual Savings (Q): **Q{financial_results['annual_savings_q']}**")
        st.write(f"• Payback Period (years): **{financial_results['payback_years']}**")
        st.write(f"• ROI (%): **{financial_results['roi_pct']}%**")
        st.write(f"• IRR (%): **{financial_results['irr_pct']}**")
        st.write(f"• CO₂ Saved (kg/year): **{financial_results['co2_saved_kg']}**")
        st.write(f"• Tree Equivalents: **{financial_results['tree_eq']}**")

    with tab2:
        st.subheader("Graphs")
        st.info("Visualizations will be added here in the next step.")
