# logic/financial/metrics_calculator.py

from config.constants import *

class FinancialMetricsCalculator:
    """
    Handles financial and environmental metric calculations.
    """

    @staticmethod
    def calculate_investment_cost(system_size_kw):
        """
        Calculates total investment cost in Q.
        """
        return round(system_size_kw * COST_PER_KW, 2)

    @staticmethod
    def calculate_annual_savings(annual_generation_kwh):
        """
        Calculates annual electricity bill savings.
        """
        return round(annual_generation_kwh * PRICE_PER_KWH, 2)

    @staticmethod
    def calculate_payback_period(investment_cost, annual_savings):
        """
        Calculates the payback period in years.
        """
        return round(investment_cost / annual_savings, 2) if annual_savings else 0

    @staticmethod
    def calculate_roi(investment_cost, annual_savings):
        """
        Calculates Return on Investment over system lifetime.
        """
        total_savings = annual_savings * SYSTEM_LIFETIME_YEARS
        return round(((total_savings - investment_cost) / investment_cost) * 100, 2)

    @staticmethod
    def calculate_co2_saved(annual_generation_kwh):
        """
        Calculates annual CO2 savings in kg.
        """
        return round(annual_generation_kwh * CO2_SAVED_PER_KWH, 2)

    @staticmethod
    def calculate_tree_equivalents(co2_saved_kg):
        """
        Calculates tree equivalents from CO2 savings.
        """
        return round((co2_saved_kg * TREE_FACTOR) / 10, 2)

    @staticmethod
    def calculate_cashflow_list(investment_cost, annual_savings, years=SYSTEM_LIFETIME_YEARS):
        """
        Returns a list of annual cash flows (year 0 = negative investment).
        """
        return [-investment_cost] + [annual_savings] * years

    @staticmethod
    def calculate_irr(cash_flows, guess=0.1):
        """
        Calculates Internal Rate of Return using Newton-Raphson method.
        """
        max_iterations = 1000
        tolerance = 1e-6
        rate = guess

        for _ in range(max_iterations):
            npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
            derivative = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))

            if derivative == 0:
                return None

            new_rate = rate - npv / derivative
            if abs(new_rate - rate) < tolerance:
                return round(new_rate * 100, 2)

            rate = new_rate

        return None
    
    @staticmethod
    def generate_cumulative_cashflow_list(investment_cost, annual_savings, years=SYSTEM_LIFETIME_YEARS):
        """
        Returns a list of cumulative cash flow values per year.
        Starts with the negative investment, then adds savings yearly.
        """
        cumulative = []
        value = -investment_cost
        for year in range(years + 1):
            if year > 0:
                value += annual_savings
            cumulative.append(round(value, 2))
        return cumulative
