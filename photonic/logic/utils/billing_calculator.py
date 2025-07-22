# logic/utils/billing_calculator.py

from photonic.config.constants import TAX_RATE
from photonic.logic.utils.data_loader import get_full_pricing_data

class BillingCalculator:
    """
    Handles the calculation of electricity bills with and without solar.
    """

    @staticmethod
    def calculate_monthly_bill(consumption_kwh, distributor, rate_type, department):
        """
        Calculates total cost of a monthly electricity bill in Q.
        Includes fixed charge, variable usage, municipal fee, and tax.
        """
        pricing = get_full_pricing_data(distributor, rate_type, department)
        if not pricing:
            return 0

        fixed = pricing["fixedCharge"]
        variable = consumption_kwh * pricing["pricePerKwh"]
        subtotal = fixed + variable
        with_municipality = subtotal * (1 + pricing["municipalityFee"])
        with_tax = with_municipality * (1 + TAX_RATE)

        return round(with_tax, 2)
      
    @staticmethod
    def generate_annual_cost_comparison(monthly_consumptions, monthly_generation, distributor, rate_type, department):
        """
        Calculates annual electricity cost without and with solar panels.
        Returns a dictionary with:
          - annual_cost_without_solar
          - annual_cost_with_solar
          - annual_savings
        """
        if len(monthly_consumptions) != 12 or len(monthly_generation) != 12:
            raise ValueError("Expected 12 months of data for both consumption and generation.")

        # Without solar
        monthly_bills_without_solar = [
            BillingCalculator.calculate_monthly_bill(kwh, distributor, rate_type, department)
            for kwh in monthly_consumptions
        ]
        annual_cost_without_solar = sum(monthly_bills_without_solar)

        # Net consumption (consumption - generation, but not below 0)
        net_monthly = [max(c - g, 0) for c, g in zip(monthly_consumptions, monthly_generation)]

        # With solar
        monthly_bills_with_solar = [
            BillingCalculator.calculate_monthly_bill(kwh, distributor, rate_type, department)
            for kwh in net_monthly
        ]
        annual_cost_with_solar = sum(monthly_bills_with_solar)

        # Savings
        annual_savings = annual_cost_without_solar - annual_cost_with_solar

        return {
            "annual_cost_without_solar": round(annual_cost_without_solar, 2),
            "annual_cost_with_solar": round(annual_cost_with_solar, 2),
            "annual_savings": round(annual_savings, 2)
        }

