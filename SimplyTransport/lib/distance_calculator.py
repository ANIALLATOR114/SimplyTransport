import math
from dataclasses import dataclass


@dataclass
class MinMaxCoordinates:
    max_latitude: float
    min_latitude: float
    max_longitude: float
    min_longitude: float


def calculate_min_max_coordinates(lat: float, lon: float, distance_in_meters: int) -> MinMaxCoordinates:
    """
    Calculate the minimum and maximum coordinates for a given latitude and longitude
    within a certain distance.
    """

    earth_radius = 6371000
    distance_in_radians = distance_in_meters / earth_radius
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    max_lat_rad = lat_rad + distance_in_radians
    min_lat_rad = lat_rad - distance_in_radians
    delta_lon = math.asin(math.sin(distance_in_radians) / math.cos(lat_rad))
    max_lon_rad = lon_rad + delta_lon
    min_lon_rad = lon_rad - delta_lon
    max_latitude = math.degrees(max_lat_rad)
    min_latitude = math.degrees(min_lat_rad)
    max_longitude = math.degrees(max_lon_rad)
    min_longitude = math.degrees(min_lon_rad)

    return MinMaxCoordinates(
        max_latitude=max_latitude,
        min_latitude=min_latitude,
        max_longitude=max_longitude,
        min_longitude=min_longitude,
    )


def distance_between_points(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points.
    """
    radius_earth = 6371  # Radius of the Earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius_earth * c  # Distance in kilometers
    return d * 1000  # Distance in meters
