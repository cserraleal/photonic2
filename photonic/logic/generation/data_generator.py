# logic/generation/data_generator.py

import random
from photonic.config.constants import (
    PANEL_POWER_KW,
    SYSTEM_EFFICIENCY,
    SYSTEM_LIFETIME_YEARS
)

class DataGenerator:
    """
    Generates realistic monthly and annual data for generation and consumption.
    """

    @staticmethod
    def simulate_monthly_distribution(total_annual_value, variation=0.05):
        """
        Generates 12 monthly values that sum up to total_annual_value with random variation.
        """
        base = total_annual_value / 12
        monthly_values = []

        for _ in range(12):
            rand_factor = 1 + random.uniform(-variation, variation)
            monthly_values.append(base * rand_factor)

        scale = total_annual_value / sum(monthly_values)
        normalized = [round(val * scale, 2) for val in monthly_values]
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
    def simulate_monthly_generation_from_irradiance(number_of_panels, monthly_irradiance_list, panel_power=PANEL_POWER_KW, efficiency=SYSTEM_EFFICIENCY):
        """
        Uses panel count and monthly irradiance to estimate monthly generation.
        """
        days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        generation = []

        for i, irradiance in enumerate(monthly_irradiance_list):
            kwh = number_of_panels * panel_power * irradiance * efficiency * days_per_month[i]
            generation.append(round(kwh, 2))

        return generation

    @staticmethod
    def simulate_annual_generation_with_degradation(base_value, years=30, degradation_rate=0.004):
        """
        Simulates annual generation with linear degradation (default 0.5% per year).
        """
        values = []
        for year in range(years):
            factor = (1 - degradation_rate) ** year
            value = round(base_value * factor, 2)
            values.append(value)
        return values
