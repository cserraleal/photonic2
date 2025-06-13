from src.calculators.environment import EnvironmentCalculator

def test_co2_saved():
    result = EnvironmentCalculator.calculate_annual_co2_saved(5000)
    assert result == 2500

def test_tree_equivalents():
    result = EnvironmentCalculator.calculate_tree_equivalents(5000)
    assert result == 200
