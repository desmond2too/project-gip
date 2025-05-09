"""
Routing module. This module provides functions for calculating routes between coordinates.
It connects to the OpenStreetMap Routing API (OSRM) for real road-based routing.
"""

import math
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OSRM API endpoint - using the public instance
OSRM_BASE_URL = "https://router.project-osrm.org/route/v1/driving/"

def get_route(start_lat, start_lng, end_lat, end_lng):
    """
    Calculate a route between two geographic coordinates using OpenStreetMap routing.
    
    Args:
        start_lat (float): Starting latitude
        start_lng (float): Starting longitude
        end_lat (float): Ending latitude
        end_lng (float): Ending longitude
        
    Returns:
        dict: Dictionary with route information
    """
    try:
        # Format coordinates for OSRM API
        coords = f"{start_lng},{start_lat};{end_lng},{end_lat}"
        
        # Build the URL (note OSRM uses lng,lat order not lat,lng)
        url = f"{OSRM_BASE_URL}{coords}?overview=full&geometries=geojson"
        
        # Make the API request
        response = requests.get(url)
        data = response.json()
        
        # Check if the route was found
        if response.status_code != 200 or data.get('code') != 'Ok':
            logger.error(f"OSRM API error: {data.get('message', 'Unknown error')}")
            return {
                'success': False,
                'error': data.get('message', 'Failed to calculate route')
            }
        
        # Extract route information
        route = data['routes'][0]
        
        # Extract the coordinates from the GeoJSON
        coordinates = route['geometry']['coordinates']
        
        # Note: OSRM returns coordinates as [longitude, latitude]
        # Convert to [latitude, longitude] for consistency with our app
        waypoints = [[point[1], point[0]] for point in coordinates]
        
        # Extract distance (in meters, convert to km) and duration (in seconds, convert to minutes)
        distance_km = route['distance'] / 1000
        duration_minutes = route['duration'] / 60
        
        return {
            'success': True,
            'distance': round(distance_km, 2),  # km
            'duration': round(duration_minutes, 2),  # minutes
            'start': [start_lat, start_lng],
            'end': [end_lat, end_lng],
            'waypoints': waypoints
        }
        
    except Exception as e:
        logger.error(f"Error calculating route: {str(e)}")
        
        # Fallback to simple calculation if the API request fails
        return fallback_route_calculation(start_lat, start_lng, end_lat, end_lng)

def fallback_route_calculation(start_lat, start_lng, end_lat, end_lng):
    """
    Fallback calculation that provides a basic straight-line route if the API fails.
    
    Args:
        start_lat (float): Starting latitude
        start_lng (float): Starting longitude
        end_lat (float): Ending latitude
        end_lng (float): Ending longitude
        
    Returns:
        dict: Dictionary with route information
    """
    # Calculate distance using Haversine formula
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers
        
        # Convert coordinates to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return distance
    
    # Calculate distance
    distance = haversine(start_lat, start_lng, end_lat, end_lng)
    
    # Generate some intermediate waypoints for a straight line
    num_points = max(3, min(20, int(distance * 2)))
    
    waypoints = []
    for i in range(num_points):
        ratio = (i + 1) / (num_points + 1)
        
        lat = start_lat + (end_lat - start_lat) * ratio
        lng = start_lng + (end_lng - start_lng) * ratio
        
        waypoints.append([lat, lng])
    
    # Estimated time based on distance (assumes 50 km/h average speed)
    duration_minutes = (distance / 50) * 60
    
    logger.warning("Using fallback routing method (straight line)")
    
    return {
        'success': True,
        'distance': round(distance, 2),  # km
        'duration': round(duration_minutes, 2),  # minutes
        'start': [start_lat, start_lng],
        'end': [end_lat, end_lng],
        'waypoints': waypoints,
        'note': 'Fallback routing used - straight line calculation'
    }