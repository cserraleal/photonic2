import json

def load_json(filepath):
    """
    Utility function to load JSON data from a file path.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- IRRADIANCE DATA ---

def get_monthly_irradiance(department, filepath='data/irradiance_monthly.json'):
    """
    Returns a list of 12 monthly irradiance values for the given department.
    """
    data = load_json(filepath)
    return data.get(department)

# --- PRICING DATA ---

def get_price_per_kwh(distributor, rate_type, department, filepath='data/pricing.json'):
    """
    Returns the price per kWh for the given location, distributor, and rate type.
    """
    data = load_json(filepath)
    try:
        return data[distributor][rate_type][department]["pricePerKwh"]
    except KeyError:
        return None

def get_full_pricing_data(distributor, rate_type, department, filepath='data/pricing.json'):
    """
    Returns full pricing information: pricePerKwh, fixedCharge, municipalityFee.
    """
    data = load_json(filepath)
    try:
        return data[distributor][rate_type][department]
    except KeyError:
        return None
