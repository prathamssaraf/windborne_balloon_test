from geopy.distance import geodesic

def find_nearby_flights(balloons, flights, threshold_km=10):
    """
    Find flights within a certain distance (threshold_km) of any balloon location.
    """
    nearby_flights = []
    for _, balloon in balloons.iterrows():
        for flight in flights:
            if flight['latitude'] and flight['longitude']:
                distance = geodesic(
                    (balloon['latitude'], balloon['longitude']),
                    (flight['latitude'], flight['longitude'])
                ).km
                if distance <= threshold_km:
                    nearby_flights.append({
                        'callsign': flight['callsign'],
                        'latitude': flight['latitude'],
                        'longitude': flight['longitude'],
                        'distance_km': distance
                    })
    return nearby_flights