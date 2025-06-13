# logic/generation/data_generator.py

import random
from config.constants import *

class DataGenerator:
    """
    Generates realistic monthly and annual data for generation and consumption.
    """

    @staticmethod
    def simulate_monthly_data_from_annual(total_annual_value, variation=0.05):
        """
        Returns 12 values that sum to total_annual_value with small random variations.
        """
        base = total_annual_value / 12
        monthly = []

        for _ in range(12):
            factor = 1 + random.uniform(-variation, variation)
            monthly.append(base * factor)

        scale = total_annual_value / sum(monthly)
        normalized = [round(val * scale, 2) for val in monthly]
        return normalized

    @staticmethod
    def simulate_annual_data_series(base_value, years=SYSTEM_LIFETIME_YEARS, variation=0.05):
        """
        Simulates yearly variation over system lifetime.
        """
        values = []

        for _ in range(years):
            factor = 1 + random.uniform(-variation, variation)
            values.append(round(base_value * factor, 2))

        return values

    @staticmethod
    def simulate_monthly_generation_from_irradiance(number_of_panels, monthly_irradiance_list):
        """
        Uses panel count and monthly irradiance to estimate monthly generation.
        """
        days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        generation = []

        for i, irradiance in enumerate(monthly_irradiance_list):
            kwh = number_of_panels * PANEL_POWER_KW * irradiance * SYSTEM_EFFICIENCY * days_per_month[i]
            generation.append(round(kwh, 2))

        return generation
