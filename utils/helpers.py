"""
Helper methods for generating realistic consumption and generation values
with slight variations for simulation and charting purposes.
"""

import random
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_realistic_monthly_data(total_annual_value, variation=0.05):
    """
    Distributes the total annual value into 12 months with slight variations.
    Ensures the final sum matches the original annual value.

    :param total_annual_value: Total yearly value (e.g., annual consumption).
    :param variation: Max % variation from base monthly average.
    :return: List of 12 monthly values.
    """
    months = 12
    base = total_annual_value / months
    monthly_values = []

    for _ in range(months):
        factor = 1 + random.uniform(-variation, variation)
        monthly_values.append(base * factor)

    # Normalize to fix rounding and keep sum equal
    total_generated = sum(monthly_values)
    scale = total_annual_value / total_generated
    scaled_values = [round(v * scale, 2) for v in monthly_values]

    logger.debug("Generated realistic monthly data.")
    return scaled_values


def generate_realistic_annual_data(base_value, years, variation=0.05):
    """
    Generates a list of yearly values with variation.

    :param base_value: The base yearly value.
    :param years: Number of years.
    :param variation: Variation % (+/-) to apply.
    :return: List of floats representing each year.
    """
    annual_values = []

    for _ in range(years):
        factor = 1 + random.uniform(-variation, variation)
        annual_values.append(round(base_value * factor, 2))

    logger.debug("Generated realistic annual data.")
    return annual_values
