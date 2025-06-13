import streamlit as st
import json
from logic.energy.consumption_calculator import ConsumptionCalculator
from logic.energy.system_calculator import SystemCalculator
from logic.financial.metrics_calculator import FinancialMetricsCalculator
from logic.generation.data_generator import DataGenerator
from logic.utils.data_loader import get_monthly_irradiance, get_price_per_kwh
from logic.utils.billing_calculator import BillingCalculator

st.set_page_config(page_title="Photonic", layout="wide")

# ----------------------------
# Sidebar Navigation
# ----------------------------

st.sidebar.title("📋 Menu")
section = st.sidebar.radio("Navigate", ["🏠 Home", "🔆 Photonic"])

# ----------------------------
# Load JSONs
# ----------------------------

@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

pricing_data = load_json("data/pricing.json")
irradiance_data = load_json("data/irradiance.json")
irradiance_monthly = load_json("data/irradiance_monthly.json")

# ----------------------------
# Page: Home
# ----------------------------

if section == "🏠 Home":
    st.title("Bienvenido a Siempre Energy")
    st.markdown("Selecciona una opción del menú para comenzar.")

# ----------------------------
# Page: Solar Calculator
# ----------------------------

elif section == "🔆 Photonic":
    if "step" not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.title("Photonic")
        st.header("Step 1: Electricity Consumption and Tariff Info")

        with st.form("step1_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: kwh1 = st.number_input("Month 1 (kWh)", min_value=0.0, step=1.0)
            with col2: kwh2 = st.number_input("Month 2 (kWh)", min_value=0.0, step=1.0)
            with col3: kwh3 = st.number_input("Month 3 (kWh)", min_value=0.0, step=1.0)
            with col4: kwh4 = st.number_input("Month 4 (kWh)", min_value=0.0, step=1.0)

            distributor = st.selectbox("Electricity Distributor", list(pricing_data.keys()))
            tariff = st.selectbox("Tariff Type", list(pricing_data[distributor].keys()))

            if st.form_submit_button("Next"):
                st.session_state.kwh = [kwh1, kwh2, kwh3, kwh4]
                st.session_state.distributor = distributor
                st.session_state.tariff = tariff
                st.session_state.step = 2
                st.rerun()

    elif st.session_state.step == 2:
        st.title("Photonic")
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
                if st.form_submit_button("Calculate"):
                    st.session_state.department = department
                    st.session_state.sizing_pref = sizing_pref
                    st.session_state.step = 3
                    st.rerun()

    elif st.session_state.step == 3:
        st.title("Photonic")
        st.success("Calculation Complete")

        kwh_list = st.session_state.kwh
        distributor = st.session_state.distributor
        rate_type = st.session_state.tariff
        dept = st.session_state.department
        pref = st.session_state.sizing_pref

        # === Energy Calculations ===
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

        # === Financial Calculations ===
        financial = BillingCalculator.generate_annual_cost_comparison(
            monthly_kwh_sim,
            monthly_generation,
            distributor,
            rate_type,
            dept
        )

        investment = FinancialMetricsCalculator.calculate_investment_cost(installed_kw)
        payback = FinancialMetricsCalculator.calculate_payback_period(investment, financial["annual_savings"])
        roi = FinancialMetricsCalculator.calculate_roi(investment, financial["annual_savings"])
        irr = FinancialMetricsCalculator.calculate_irr(
            FinancialMetricsCalculator.calculate_cashflow_list(investment, financial["annual_savings"])
        )
        co2 = FinancialMetricsCalculator.calculate_co2_saved(annual_gen)
        trees = FinancialMetricsCalculator.calculate_tree_equivalents(co2)

        # === Display Results ===
        tab1, tab2 = st.tabs(["📋 Numeric Results", "📈 Graphs"])

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
