"""
Utility functions for NYC Live Aircraft Tracker.
Provides geospatial calculations and unit conversions.
"""

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
    
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two points.
    
    Args:
        lat1, lon1: Coordinates of first point (home)
        lat2, lon2: Coordinates of second point (aircraft)
    
    Returns:
        Bearing in degrees (0-360), where 0 is North
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Calculate bearing
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    initial_bearing = math.atan2(x, y)
    
    # Convert to degrees and normalize to 0-360
    bearing = (math.degrees(initial_bearing) + 360) % 360
    
    return bearing


def meters_to_feet(meters):
    """Convert meters to feet."""
    if meters is None:
        return None
    return meters * 3.28084


def mps_to_kmh(mps):
    """Convert meters per second to kilometers per hour."""
    if mps is None:
        return None
    return mps * 3.6


def is_in_bearing_range(bearing, min_bearing, max_bearing):
    """
    Check if a bearing falls within a specified range.
    
    Args:
        bearing: The bearing to check (0-360)
        min_bearing: Minimum bearing of the range
        max_bearing: Maximum bearing of the range
    
    Returns:
        True if bearing is in range, False otherwise
    """
    if bearing is None:
        return False
    
    # Handle the simple case where range doesn't cross 0°
    if min_bearing <= max_bearing:
        return min_bearing <= bearing <= max_bearing
    else:
        # Handle case where range crosses 0° (e.g., 350° to 10°)
        return bearing >= min_bearing or bearing <= max_bearing
