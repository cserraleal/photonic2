import pytest
from src.calculators.energy import EnergyCalculator

def test_average_monthly_consumption():
    result = EnergyCalculator.calculate_average_monthly_consumption([100, 150, 120, 130])
    assert result == 125.0

def test_required_system_size_kw():
    result = EnergyCalculator.calculate_required_system_size_kw(300, 5.2)
    assert round(result, 2) == 2.43  # Adjust based on expected formula result

def test_number_of_panels():
    result = EnergyCalculator.calculate_number_of_panels(3.2)
    assert result == 6

def test_installed_power_kw():
    result = EnergyCalculator.calculate_installed_power_kw(10)
    assert round(result, 2) == 6.1

def test_required_area_m2():
    result = EnergyCalculator.calculate_required_area_m2(5)
    assert result == 13.5

def test_annual_generation_kwh():
    result = EnergyCalculator.calculate_annual_generation_kwh(5, 5.0)
    assert round(result, 2) == 4341.68
