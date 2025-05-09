"""
Geocoding module.
This module provides functions for geocoding addresses to coordinates.
In a production environment, this would connect to a real geocoding API.
"""

# Sample geocoding data for common locations in Namibia
GEOCODING_SAMPLES = {
    'windhoek': {'lat': -22.559, 'lng': 17.083},
    'swakopmund': {'lat': -22.6784, 'lng': 14.5258},
    'walvis bay': {'lat': -22.9576, 'lng': 14.5065},
    'otjiwarongo': {'lat': -20.4637, 'lng': 16.6477},
    'keetmanshoop': {'lat': -26.5833, 'lng': 18.1333},
    'rundu': {'lat': -17.9333, 'lng': 19.7667},
    'oshakati': {'lat': -17.7883, 'lng': 15.7044},
    'katima mulilo': {'lat': -17.5, 'lng': 24.2667},
    'gobabis': {'lat': -22.45, 'lng': 18.9667},
    'okahandja': {'lat': -21.9833, 'lng': 16.9167},
}

def geocode_location(location_query):
    """
    Convert a location string to geographic coordinates.
    
    Args:
        location_query (str): The location to geocode
        
    Returns:
        dict: Dictionary with lat and lng keys for the coordinates
    """
    
  
    
    # Simple lookup - check if the query matches any of our sample locations
    location_query = location_query.lower()
    
    for location, coordinates in GEOCODING_SAMPLES.items():
        if location_query in location or location in location_query:
            return {
                'success': True,
                'lat': coordinates['lat'],
                'lng': coordinates['lng'],
                'formatted_address': location.title()
            }
    
    # Default to Windhoek if no match is found
    return {
        'success': False,
        'lat': -22.559,
        'lng': 17.083,
        'formatted_address': 'Location not found. Showing Windhoek.',
        'error': 'Location not found'
    }