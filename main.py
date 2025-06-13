# main.py

from logic.energy.consumption_calculator import ConsumptionCalculator
from logic.energy.system_calculator import SystemCalculator
from logic.financial.metrics_calculator import FinancialMetricsCalculator
from logic.generation.data_generator import DataGenerator
from logic.utils.data_loader import get_monthly_irradiance, get_price_per_kwh
from logic.utils.billing_calculator import BillingCalculator

import matplotlib.pyplot as plt
import numpy as np

# === USER INPUTS ===
monthly_kwh_input = [240, 250, 260, 255]  # kWh values
department = "Guatemala"
distributor = "EGGSA"
rate_type = "BT"
sizing_preference = "Balanced"

# === LOAD EXTERNAL DATA ===
monthly_irradiance = get_monthly_irradiance(department)
if monthly_irradiance is None:
    raise ValueError(f"Missing irradiance data for department: {department}")

price_per_kwh = get_price_per_kwh(distributor, rate_type, department)
if price_per_kwh is None:
    raise ValueError(f"Missing price data for {distributor}/{rate_type}/{department}")

# === STEP 1: CONSUMPTION CALCULATIONS ===
avg_monthly_kwh = ConsumptionCalculator.calculate_average_monthly_consumption(monthly_kwh_input)
annual_kwh = ConsumptionCalculator.calculate_annual_consumption(avg_monthly_kwh)
monthly_consumption_sim = DataGenerator.simulate_monthly_distribution(annual_kwh)

# === STEP 2: SYSTEM SIZING ===
annual_irradiance = sum(monthly_irradiance) / 12
system_kw = SystemCalculator.calculate_required_system_size_kw(avg_monthly_kwh, annual_irradiance)
panels = SystemCalculator.calculate_number_of_panels(system_kw)
installed_kw = SystemCalculator.calculate_installed_power_kw(panels)
area_m2 = SystemCalculator.calculate_required_area_m2(panels)
annual_generation = SystemCalculator.calculate_annual_generation_kwh(panels, annual_irradiance)
coverage = SystemCalculator.calculate_coverage_percentage(annual_generation, avg_monthly_kwh, sizing_preference)
monthly_generation_sim = DataGenerator.simulate_monthly_generation_from_irradiance(panels, monthly_irradiance)

# === STEP 3: ENVIRONMENTAL IMPACT ===
co2_saved = FinancialMetricsCalculator.calculate_co2_saved(annual_generation)
trees = FinancialMetricsCalculator.calculate_tree_equivalents(co2_saved)

# === STEP 4: FINANCIAL METRICS ===
financial_data = BillingCalculator.generate_annual_cost_comparison(
    monthly_consumption_sim,
    monthly_generation_sim,
    distributor,
    rate_type,
    department
)

annual_cost_without_solar = financial_data["annual_cost_without_solar"]
annual_cost_with_solar = financial_data["annual_cost_with_solar"]
annual_savings = financial_data["annual_savings"]

investment = FinancialMetricsCalculator.calculate_investment_cost(installed_kw)
payback = FinancialMetricsCalculator.calculate_payback_period(investment, annual_savings)
roi = FinancialMetricsCalculator.calculate_roi(investment, annual_savings)
cashflow = FinancialMetricsCalculator.calculate_cashflow_list(investment, annual_savings)
irr = FinancialMetricsCalculator.calculate_irr(cashflow)
cumulative_cashflow = FinancialMetricsCalculator.generate_cumulative_cashflow_list(investment, annual_savings)

# === STEP 5: ANNUAL SIMULATIONS ===
annual_consumption_series = DataGenerator.simulate_annual_data_series(annual_kwh)
annual_generation_series = DataGenerator.simulate_annual_data_series(annual_generation)

# === OUTPUTS ===
print("==== SYSTEM SIZING ====")
print(f"Avg. Monthly Consumption (kWh): {avg_monthly_kwh}")
print(f"Annual Consumption (kWh): {annual_kwh}")
print(f"System Size (kW): {system_kw}")
print(f"Panels Required: {panels}")
print(f"Installed Power (kW): {installed_kw}")
print(f"Required Area (m²): {area_m2}")
print(f"Annual Generation (kWh): {annual_generation}")
print(f"Coverage (%): {coverage}")

print("\n==== ENVIRONMENTAL IMPACT ====")
print(f"CO2 Saved (kg/year): {co2_saved}")
print(f"Tree Equivalents: {trees}")

print("\n==== FINANCIAL ====")
print(f"Annual Bill Without Solar (Q): {annual_cost_without_solar}")
print(f"Annual Bill With Solar (Q): {annual_cost_with_solar}")
print(f"Annual Savings (Q): {annual_savings}")
print(f"Investment Cost (Q): {investment}")
print(f"Payback Period (years): {payback}")
print(f"ROI (%): {roi}")
print(f"IRR (%): {irr}")

print("\n==== SIMULATED DATA ====")
print("Monthly Consumption (kWh):", monthly_consumption_sim)
print("Monthly Generation (kWh):", monthly_generation_sim)
print("Annual Consumption Series:", annual_consumption_series)
print("Annual Generation Series:", annual_generation_series)

# === PLOT 1: Monthly Energy Comparison ===
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
x = np.arange(12)
width = 0.35

plt.figure(figsize=(10, 5))
plt.bar(x - width/2, monthly_consumption_sim, width, label="Consumption (kWh)", color="skyblue")
plt.bar(x + width/2, monthly_generation_sim, width, label="Generation (kWh)", color="orange")
plt.title("Monthly Energy Consumption vs Generation")
plt.xlabel("Month")
plt.ylabel("Energy (kWh)")
plt.xticks(x, months)
plt.legend()
plt.grid(True, axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()

# === PLOT 2: Cumulative Cash Flow ===
plt.figure(figsize=(10, 5))
plt.plot(cumulative_cashflow, marker='o', color='green')
plt.title("Cumulative Cash Flow Over System Lifetime")
plt.xlabel("Year")
plt.ylabel("Cumulative Value (Q)")
plt.xticks(range(len(cumulative_cashflow)))
plt.grid(True)
plt.tight_layout()
plt.show()
