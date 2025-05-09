"""
Property search module.
This module provides functions for searching properties based on criteria.
"""

def search_properties(criteria, properties):
    """
    Search properties based on specified criteria.
    
    Args:
        criteria (dict): Search criteria including:
            - location (str): Location search string
            - property_types (list): List of property types to include
            - deal_types (list): List of deal types (sale, rent)
            - min_price (float): Minimum price
            - max_price (float): Maximum price
            - bedrooms (int): Minimum number of bedrooms
            - bathrooms (int): Minimum number of bathrooms
            - proximities (list): List of nearby amenities
            
        properties (list): List of property objects to search through
    
    Returns:
        list: Filtered list of properties matching criteria
    """
    results = []
    
    # Extract search criteria with defaults
    location = criteria.get('location', '').lower()
    property_types = criteria.get('property_types', [])
    deal_types = criteria.get('deal_types', [])
    min_price = float(criteria.get('min_price', 0))
    max_price = float(criteria.get('max_price', float('inf')))
    bedrooms = int(criteria.get('bedrooms', 0))
    bathrooms = int(criteria.get('bathrooms', 0))
    proximities = criteria.get('proximities', [])
    
    for property in properties:
        # Skip if property doesn't match any selected type
        if property_types and property['type'] not in property_types:
            continue
            
        # Skip if property doesn't match any selected deal type
        if deal_types and property['dealType'] not in deal_types:
            continue
            
        # Skip if price is outside range
        if property['price'] < min_price or property['price'] > max_price:
            continue
            
        # Skip if doesn't meet minimum bedrooms/bathrooms
        if property.get('bedrooms', 0) < bedrooms:
            continue
            
        if property.get('bathrooms', 0) < bathrooms:
            continue
            
        # Check location match if specified
        if location and location not in property.get('address', '').lower():
            # Could be expanded to check coordinates against a geographic area
            continue
            
        # Check proximity requirements
        # For this demo, we'll assume all properties meet proximity requirements
        
        results.append(property)
    
    return results