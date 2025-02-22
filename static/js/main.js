let map;
let markers = [];

function initializeMap(balloons) {
    map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(map);

    // Add balloons to the map
    if (Array.isArray(balloons)) {
        balloons.forEach((balloon, index) => {
            if (balloon.latitude && balloon.longitude) {
                const marker = L.circleMarker([balloon.latitude, balloon.longitude], { color: 'blue' })
                    .bindPopup(`Balloon ${index + 1}: (${balloon.latitude}, ${balloon.longitude})`);
                marker.addTo(map);
                markers.push(marker);
            }
        });
    }
}

function highlightBalloonAndFetchFlights(balloon) {
    // Clear existing markers
    markers.forEach(marker => marker.remove());
    markers = [];

    // Highlight the selected balloon
    const selectedMarker = L.circleMarker([balloon.latitude, balloon.longitude], { color: 'green' })
        .bindPopup(`Balloon: (${balloon.latitude}, ${balloon.longitude})`);
    selectedMarker.addTo(map);
    markers.push(selectedMarker);

    // Center the map on the selected balloon
    map.setView([balloon.latitude, balloon.longitude], 5);

    // Fetch nearby flights
    fetch(`/nearby-flights/${balloon.latitude}/${balloon.longitude}`)
        .then(response => response.json())
        .then(flights => {
            // Clear existing flight markers
            map.eachLayer(layer => {
                if (layer instanceof L.Marker && layer.options.icon) {
                    map.removeLayer(layer);
                }
            });

            // Add flight markers to the map
            flights.forEach(flight => {
                const flightIcon = L.icon({
                    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                });
                L.marker([flight.latitude, flight.longitude], { icon: flightIcon })
                    .bindPopup(`Flight: ${flight.callsign} (${flight.distance_km} km away)`)
                    .addTo(map);
            });
        })
        .catch(error => console.error("Error fetching nearby flights:", error));
}