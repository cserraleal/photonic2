# main.py

from logic.energy.consumption_calculator import ConsumptionCalculator
from logic.energy.system_calculator import SystemCalculator
from logic.financial.metrics_calculator import FinancialMetricsCalculator
from logic.generation.data_generator import DataGenerator
from config.constants import *

# === INPUTS ===
bills_q = [450, 460, 440, 455]
annual_irradiance = 5.3  # kWh/m²/day
monthly_irradiance = [5.1, 5.3, 5.6, 5.8, 5.9, 6.0, 5.8, 5.6, 5.4, 5.2, 5.0, 4.9]
sizing_preference = "Balanced"

# === STEP 1: CONSUMPTION CALCULATION ===
monthly_kwh = [ConsumptionCalculator.calculate_monthly_kwh(bill) for bill in bills_q]
avg_monthly_kwh = ConsumptionCalculator.calculate_average_monthly_consumption(monthly_kwh)
annual_kwh = ConsumptionCalculator.calculate_annual_consumption(avg_monthly_kwh)

# === STEP 2: SYSTEM SIZING ===
system_kw = SystemCalculator.calculate_required_system_size_kw(avg_monthly_kwh, annual_irradiance)
panels = SystemCalculator.calculate_number_of_panels(system_kw)
installed_kw = SystemCalculator.calculate_installed_power_kw(panels)
area_m2 = SystemCalculator.calculate_required_area_m2(panels)
annual_generation = SystemCalculator.calculate_annual_generation_kwh(panels, annual_irradiance)
coverage = SystemCalculator.calculate_coverage_percentage(annual_generation, avg_monthly_kwh, sizing_preference)

# === STEP 3: ENVIRONMENTAL IMPACT ===
co2_saved = FinancialMetricsCalculator.calculate_co2_saved(annual_generation)
trees = FinancialMetricsCalculator.calculate_tree_equivalents(co2_saved)

# === STEP 4: FINANCIAL METRICS ===
investment = FinancialMetricsCalculator.calculate_investment_cost(system_kw)
annual_savings = FinancialMetricsCalculator.calculate_annual_savings(annual_generation)
payback = FinancialMetricsCalculator.calculate_payback_period(investment, annual_savings)
roi = FinancialMetricsCalculator.calculate_roi(investment, annual_savings)
cashflow = FinancialMetricsCalculator.calculate_cashflow_list(investment, annual_savings)
irr = FinancialMetricsCalculator.calculate_irr(cashflow)

# === STEP 5: SIMULATION ===
monthly_consumption_sim = ConsumptionCalculator.simulate_monthly_consumption(avg_monthly_kwh)
monthly_generation_sim = DataGenerator.simulate_monthly_generation_from_irradiance(panels, monthly_irradiance)
annual_consumption_series = DataGenerator.simulate_annual_data_series(annual_kwh)
annual_generation_series = DataGenerator.simulate_annual_data_series(annual_generation)

# === OUTPUT ===
print("==== SYSTEM SIZING ====")
print(f"Average Monthly Consumption (kWh): {avg_monthly_kwh}")
print(f"Annual Consumption (kWh): {annual_kwh}")
print(f"Required System Size (kW): {system_kw}")
print(f"Number of Panels: {panels}")
print(f"Installed Power (kW): {installed_kw}")
print(f"Required Area (m²): {area_m2}")
print(f"Annual Generation (kWh): {annual_generation}")
print(f"Coverage (%): {coverage}")

print("\n==== ENVIRONMENT ====")
print(f"CO₂ Saved (kg): {co2_saved}")
print(f"Tree Equivalents: {trees}")

print("\n==== FINANCIAL ====")
print(f"Investment Cost (Q): {investment}")
print(f"Annual Savings (Q): {annual_savings}")
print(f"Payback Period (years): {payback}")
print(f"ROI (%): {roi}")
print(f"IRR (%): {irr}")

print("\n==== SIMULATED DATA ====")
print("Monthly Consumption (kWh):", monthly_consumption_sim)
print("Monthly Generation (kWh):", monthly_generation_sim)
print("Annual Consumption Series:", annual_consumption_series)
print("Annual Generation Series:", annual_generation_series)
