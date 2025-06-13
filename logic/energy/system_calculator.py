# logic/energy/system_calculator.py

from math import ceil
from config.constants import *

class SystemCalculator:
    """
    Handles calculations related to system sizing, generation, and area.
    """

    @staticmethod
    def calculate_required_system_size_kw(avg_monthly_kwh, annual_irradiance):
        """
        Calculates required system size in kW.
        """
        return round((avg_monthly_kwh * 12) / (annual_irradiance * 365 * SYSTEM_EFFICIENCY), 2)

    @staticmethod
    def calculate_number_of_panels(system_size_kw):
        """
        Calculates the number of panels required (rounded up).
        """
        return ceil(system_size_kw / PANEL_POWER_KW)

    @staticmethod
    def calculate_installed_power_kw(number_of_panels):
        """
        Calculates total installed power in kW.
        """
        return round(number_of_panels * PANEL_POWER_KW, 2)

    @staticmethod
    def calculate_required_area_m2(number_of_panels):
        """
        Calculates required roof area in square meters.
        """
        return round(number_of_panels * PANEL_AREA_M2, 2)

    @staticmethod
    def calculate_annual_generation_kwh(number_of_panels, annual_irradiance):
        """
        Calculates annual energy generation in kWh.
        """
        return round(number_of_panels * PANEL_POWER_KW * SYSTEM_EFFICIENCY * annual_irradiance * 365, 2)

    @staticmethod
    def calculate_coverage_percentage(annual_generation_kwh, avg_monthly_kwh, sizing_preference):
        """
        Calculates coverage percentage, capped at 100 if balanced.
        """
        coverage = (annual_generation_kwh / (avg_monthly_kwh * 12)) * 100
        return round(min(coverage, 100.0), 2) if sizing_preference.lower() == "balanced" else round(coverage, 2)
