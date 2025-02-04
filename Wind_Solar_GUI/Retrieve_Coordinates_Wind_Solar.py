import requests

def get_coordinates_wind_solar(city, state, country):
    """Retrieve coordinates for the given city, state, and country."""
    api_key = "pk.06116c260378fbaf82bb1d519c2e0e2d"
    base_url = "https://us1.locationiq.com/v1/search.php"

    location_str = f"{city}, {state}, {country}"

    params = {
        'key': api_key,
        'q': location_str,
        'format': 'json'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()
        if data:
            # Get the latitude and longitude from the response
            lat_2 = float(data[0]['lat'])
            lon_2 = float(data[0]['lon'])
            return lat_2, lon_2
        else:
            return None, None
        
    except requests.exceptions.RequestException:
        return None, None

