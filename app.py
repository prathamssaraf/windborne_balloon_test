from flask import Flask, render_template, jsonify, request
from utils.balloon_api import fetch_balloon_data, clean_balloon_data
from utils.flight_api import fetch_nearby_flights
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Get OpenSky credentials from environment variables
OPENSKY_USERNAME = os.getenv('OPENSKY_USERNAME')
OPENSKY_PASSWORD = os.getenv('OPENSKY_PASSWORD')

@app.route('/')
def index():
    try:
        # Fetch and process balloon data
        balloon_df = fetch_balloon_data()
        balloon_df = clean_balloon_data(balloon_df)
        
        # Convert data to JSON for visualization
        balloons_json = balloon_df.to_dict(orient='records') if not balloon_df.empty else []
        
        return render_template('index.html', balloons=balloons_json)
    except Exception as e:
        # If balloon data fetch fails, return empty list
        print(f"Error fetching balloon data: {e}")
        return render_template('index.html', balloons=[])

@app.route('/fetch_nearby_flights')
def get_nearby_flights():
    """
    API endpoint to fetch nearby flights for a given balloon location.
    """
    try:
        # Get latitude and longitude from query parameters
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({
            'success': False,
            'error': 'Invalid latitude or longitude parameters'
        }), 400

    if not OPENSKY_USERNAME or not OPENSKY_PASSWORD:
        return jsonify({
            'success': False,
            'error': 'OpenSky Network credentials not configured'
        }), 500

    try:
        nearby_flights = fetch_nearby_flights(
            balloon_latitude=latitude,
            balloon_longitude=longitude,
            username=OPENSKY_USERNAME,
            password=OPENSKY_PASSWORD,
            threshold_km=100
        )
        
        return jsonify({
            'success': True,
            'flights': nearby_flights
        })
    except Exception as e:
        print(f"Error fetching nearby flights: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)