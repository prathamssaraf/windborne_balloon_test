import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://a.windbornesystems.com/treasure/"

def fetch_balloon_data():
    """
    Fetch and process balloon data for the last 24 hours.
    """
    all_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    current_time = datetime.utcnow()

    for hour in range(24):
        url = f"{BASE_URL}{hour:02d}.json"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            try:
                data = response.json()
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, list) and len(entry) >= 3:
                            try:
                                lat = float(entry[0])
                                lon = float(entry[1])
                                alt = float(entry[2])
                                timestamp = current_time - timedelta(hours=hour)
                                all_data.append({
                                    'latitude': lat,
                                    'longitude': lon,
                                    'altitude': alt,
                                    'timestamp': timestamp.isoformat()
                                })
                            except (ValueError, TypeError, IndexError):
                                print(f"Invalid entry values in {url}: {entry}")
                        else:
                            print(f"Invalid entry format in {url}: {entry}")
                else:
                    print(f"Unexpected data format in {url} - Top-level is not a list")
            except ValueError:
                print(f"Malformed JSON in {url}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

    return pd.DataFrame(all_data)

def clean_balloon_data(df):
    """
    Clean and validate balloon data.
    """
    if df.empty:
        return df

    df = df.apply(pd.to_numeric, errors='ignore')
    df = df.dropna(subset=['latitude', 'longitude', 'altitude'])

    df = df.query(
        "-90 <= latitude <= 90 and "
        "-180 <= longitude <= 180 and "
        "altitude >= 0"
    )

    return df