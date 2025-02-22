import requests
from geopy.distance import geodesic

# Function to fetch real-time flight data from OpenSky Network
def fetch_nearby_flights(balloon_latitude, balloon_longitude, threshold_km=10):
    # OpenSky API endpoint
    url = "https://opensky-network.org/api/states/all"
    
    try:
        # Fetch flight data
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching flight data: {response.status_code}")
            return []

        data = response.json()
        nearby_flights = []

        # Process flight data
        if 'states' in data:
            for state in data['states']:
                try:
                    # Extract relevant fields
                    callsign = state[1].strip() if state[1] else "Unknown"
                    latitude = float(state[6]) if state[6] else None
                    longitude = float(state[5]) if state[5] else None
                    altitude = float(state[7]) if state[7] else None

                    # Skip invalid coordinates
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
                            'distance_km': round(distance_km, 2)
                        })
                except (ValueError, TypeError, IndexError):
                    continue

        return nearby_flights

    except Exception as e:
        print(f"Error: {e}")
        return []

# Example usage
if __name__ == "__main__":
    # Balloon coordinates (example)
    
    balloon_latitude = 42.07416481108947  # Latitude of San Francisco
    balloon_longitude =  28.350676433280547  # Longitude of San Francisco

    # Find nearby flights
    nearby_flights = fetch_nearby_flights(balloon_latitude, balloon_longitude, threshold_km=100)

    # Print results
    if nearby_flights:
        print("Nearby Flights:")
        for flight in nearby_flights:
            print(f"Callsign: {flight['callsign']}, "
                  f"Latitude: {flight['latitude']}, "
                  f"Longitude: {flight['longitude']}, "
                  f"Altitude: {flight['altitude']} meters, "
                  f"Distance: {flight['distance_km']} km")
    else:
        print("No nearby flights found.")