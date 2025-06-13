from src.calculators.financial import FinancialCalculator

def test_investment_cost():
    result = FinancialCalculator.calculate_investment_cost(4)
    assert result == 30000.0

def test_payback_period():
    result = FinancialCalculator.calculate_payback_period(30000, 6000)
    assert result == 5.0

def test_roi():
    result = FinancialCalculator.calculate_roi_percent(30000, 6000)
    assert result == 400.0

def test_irr():
    cashflows = [-30000] + [6000] * 25
    result = FinancialCalculator.calculate_irr(cashflows)
    assert 0.18 <= result <= 0.22  # IRR should be in this range

def test_cashflow():
    cashflow = FinancialCalculator.generate_cumulative_cashflow(10000, 2500, years=3)
    assert cashflow == [
        (0, -10000),
        (1, -7500),
        (2, -5000),
        (3, -2500)
    ]
