# logic/energy/consumption_calculator.py

import random

class ConsumptionCalculator:
    """
    Handles calculations and simulations related to electricity consumption.
    """

    @staticmethod
    def calculate_average_monthly_consumption(monthly_kwh_list):
        """
        Calculates the average of given monthly consumption values in kWh.
        """
        return sum(monthly_kwh_list) / len(monthly_kwh_list)

    @staticmethod
    def calculate_annual_consumption(avg_monthly_kwh):
        """
        Estimates annual consumption from average monthly value.
        """
        return avg_monthly_kwh * 12

    @staticmethod
    def simulate_monthly_consumption(avg_monthly_kwh, variation=0.05):
        """
        Simulates 12 months of consumption with realistic variation.
        Ensures the total equals the expected annual value.
        """
        base = avg_monthly_kwh
        values = []

        for _ in range(12):
            factor = 1 + random.uniform(-variation, variation)
            values.append(base * factor)

        total = sum(values)
        scale = (avg_monthly_kwh * 12) / total
        adjusted = [v * scale for v in values]

        return adjusted
