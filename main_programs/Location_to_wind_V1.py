import requests



def get_coordinates(self, city, state, country):
        """Retrieve coordinates for the given city, state, and country."""
        # LocationIQ API key (insert your API key here)
        self.api_key = "pk.06116c260378fbaf82bb1d519c2e0e2d"
        self.base_url = "https://us1.locationiq.com/v1/search.php"

        location_str = f"{city}, {state}, {country}"

        params = {
            'key': self.api_key,
            'q': location_str,
            'format': 'json'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            data = response.json()
            if data:
                # Get the latitude and longitude from the response
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                return latitude,longitude
            else:
                return None, None
        except requests.exceptions.RequestException as e:
            return None, None