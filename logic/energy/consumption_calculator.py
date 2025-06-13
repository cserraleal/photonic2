# logic/energy/consumption_calculator.py

import random
from config.constants import *

class ConsumptionCalculator:
    """
    Handles calculations and simulations related to electricity consumption.
    """

    @staticmethod
    def calculate_monthly_kwh(bill_q):
        """
        Converts bill amount in Q to energy consumption in kWh.
        """
        return round(bill_q / PRICE_PER_KWH, 2)

    @staticmethod
    def calculate_average_monthly_consumption(monthly_kwh_list):
        """
        Calculates the average of 4 monthly consumption values in kWh.
        """
        return round(sum(monthly_kwh_list) / len(monthly_kwh_list), 2)

    @staticmethod
    def calculate_annual_consumption(avg_monthly_kwh):
        """
        Estimates annual consumption from average monthly value.
        """
        return round(avg_monthly_kwh * 12, 2)

    @staticmethod
    def simulate_monthly_consumption(avg_monthly_kwh, variation=0.05):
        """
        Simulates 12 months of consumption with realistic variation.
        Total is normalized to match annual average × 12.
        """
        base = avg_monthly_kwh
        values = []

        for _ in range(12):
            factor = 1 + random.uniform(-variation, variation)
            values.append(base * factor)

        # Normalize to ensure correct annual total
        total = sum(values)
        scale = (avg_monthly_kwh * 12) / total
        adjusted = [round(v * scale, 2) for v in values]

        return adjusted
