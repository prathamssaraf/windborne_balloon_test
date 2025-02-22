import requests
from geopy.distance import geodesic
from requests.auth import HTTPBasicAuth

def fetch_nearby_flights(balloon_latitude, balloon_longitude, username, password, threshold_km=100):
    """
    Fetch nearby flights within a certain distance from the balloon's location.
    
    Args:
        balloon_latitude (float): Balloon's latitude
        balloon_longitude (float): Balloon's longitude
        username (str): OpenSky Network username
        password (str): OpenSky Network password
        threshold_km (float): Distance threshold in kilometers (default: 10)
        
    Returns:
        list: List of dictionaries containing nearby flight information
    """
    url = "https://opensky-network.org/api/states/all"
    
    try:
        # Add authentication
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            timeout=30  # Add timeout to prevent hanging
        )
        
        # Handle different HTTP status codes
        if response.status_code == 404:
            print("API endpoint not found. Please check the URL.")
            return []
        elif response.status_code == 401:
            print("Authentication failed. Please check your username and password.")
            return []
        elif response.status_code == 429:
            print("Too many requests. Please try again later.")
            return []
        elif response.status_code != 200:
            print(f"Error fetching flight data: Status code {response.status_code}")
            return []

        data = response.json()
        nearby_flights = []

        if 'states' not in data:
            print("No flight state data available")
            return []

        for state in data['states']:
            try:
                # OpenSky API returns data in a specific order
                # [icao24, callsign, origin_country, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, heading, vertical_rate, sensors, geo_altitude, squawk, spi, position_source]
                callsign = state[1].strip() if state[1] else "Unknown"
                latitude = float(state[6]) if state[6] else None
                longitude = float(state[5]) if state[5] else None
                altitude = float(state[7]) if state[7] else None
                velocity = float(state[9]) if state[9] else None
                heading = float(state[10]) if state[10] else None

                if latitude is None or longitude is None:
                    continue

                # Calculate distance between balloon and aircraft
                balloon_coords = (balloon_latitude, balloon_longitude)
                aircraft_coords = (latitude, longitude)
                distance_km = geodesic(balloon_coords, aircraft_coords).km

                # Check if the aircraft is within the threshold distance
                if distance_km <= threshold_km:
                    nearby_flights.append({
                        'callsign': callsign,
                        'latitude': latitude,
                        'longitude': longitude,
                        'altitude': altitude,
                        'velocity': velocity,
                        'heading': heading,
                        'distance_km': round(distance_km, 2)
                    })
            except (ValueError, TypeError, IndexError) as e:
                print(f"Error processing flight data: {e}")
                continue

        return nearby_flights

    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching nearby flights: {e}")
        return []