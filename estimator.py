"""Property price estimation module for Namibia.
This module implements a simplified regression model for estimating property prices in Namibian Dollars."""

def estimate_price(features):
    """
    Estimate property price based on input features.
    
    Args:
        features (dict): A dictionary containing property features:
            - property_type (str): Type of property (apartment, house, etc.)
            - location (str): Location of the property
            - bedrooms (int): Number of bedrooms
            - bathrooms (int): Number of bathrooms
            - area (float): Area in square meters
            - age (int): Age of property in years
            - condition (str): Condition of property (excellent, good, fair, poor)
            - garage (bool): Whether property has a garage
            - pool (bool): Whether property has a pool
            - garden (bool): Whether property has a garden
            - security (bool): Whether property has a security system
            - aircon (bool): Whether property has air conditioning
            - furnished (bool): Whether property is furnished
    
    Returns:
        float: Estimated price of the property in Namibian Dollars
    """
    # Base price based on property type in Namibian
    base_prices = {
        'apartment': 200000,
        'house': 500000,
        'townhouse': 300000,
        'villa': 700000,
        'commercial': 900000
    }
    
    # Get base price for property type or use a default
    base_price = base_prices.get(features['property_type'], 550000)
    
    # Area multiplier (price per square meter) - adjusted for Namibian market
    area_multiplier = 2500
    
    # Adjust for location (simplified, using Namibian cities)
    location_multipliers = {
        'windhoek': 1.5,        # Capital city premium
        'swakopmund': 1.4,      # Coastal premium
        'walvis bay': 1.3,      # Port city premium
        'otjiwarongo': 0.8,     # Smaller city discount
        'keetmanshoop': 0.7,    # Rural discount
        'oshakati': 0.9,
        'rundu': 0.75,
        'katima mulilo': 0.7,
        'henties bay': 1.2,     # Coastal premium
        'okahandja': 0.85,
        'grootfontein': 0.75,
        'lüderitz': 1.1,        # Coastal premium
        'ondangwa': 0.85
    }
    
    # Default to 1.0 if location not in our database
    location_factor = 1.0
    if features['location'].lower() in location_multipliers:
        location_factor = location_multipliers[features['location'].lower()]
    
    # Adjust for bedrooms and bathrooms (higher values for Namibian market)
    bedroom_value = features['bedrooms'] * 60000
    bathroom_value = features['bathrooms'] * 45000
    
    # Adjust for property age (newer properties cost more)
    age_factor = max(0.65, 1 - (features['age'] * 0.015))  # Steeper depreciation, minimum 65% of value
    
    # Adjust for condition
    condition_factors = {
        'excellent': 1.2,
        'good': 1.0,
        'fair': 0.8,
        'poor': 0.6
    }
    condition_factor = condition_factors.get(features['condition'], 1.0)
    
    # Adjust for additional features - higher values for Namibian market
    feature_value = 0
    if features.get('garage', False):
        feature_value += 60000     # Parking is valuable
    if features.get('pool', False):
        feature_value += 120000    # Pools are premium features in Namibia
    if features.get('garden', False):
        feature_value += 40000     # Gardens are desirable
    if features.get('security', False):
        feature_value += 80000     # Security is highly valued
    if features.get('aircon', False):
        feature_value += 30000     # Important in hot climate
    if features.get('furnished', False):
        feature_value += 100000    # Furnished properties command premium
    
    # Calculate area value with a minimum area consideration
    min_area_value = 100 * area_multiplier  # Minimum area calculation
    area_value = max(min_area_value, features['area'] * area_multiplier)
    
    # Calculate final price
    estimated_price = (
        (base_price + area_value + bedroom_value + bathroom_value + feature_value) *
        location_factor * age_factor * condition_factor
    )
    
    # Round to nearest thousand
    return round(estimated_price / 1000) * 1000