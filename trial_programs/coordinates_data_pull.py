import requests
import csv

def get_solar_data(latitude, longitude, api_key, output_file):
    """Fetch solar data from the NREL API based on latitude and longitude and export to CSV."""
    
    # NREL API URL for solar resource data
    url = f"https://developer.nrel.gov/api/solar/solar_resource/v1.json?api_key={api_key}&lat={latitude}&lon={longitude}"

    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

        # Parse the JSON response
        data = response.json()

        # Check if the response contains solar data
        if 'outputs' in data:
            solar_data = data['outputs']

            # Prepare data for CSV
            csv_data = {
                "Latitude": latitude,
                "Longitude": longitude,
                "Average Direct Normal Irradiance (kWh/m^2/d)": solar_data['avg_dni'],
                "Average Global Horizontal Irradiance (kWh/m^2/d)": solar_data['avg_ghi'],
                "Average Tilt at Latitude (kWh/m^2/d)": solar_data['avg_lat_tilt']
            }

            # Write data to CSV
            with open(output_file, mode='w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())
                writer.writeheader()
                writer.writerow(csv_data)

            print(f"Solar data exported to {output_file}.")
        else:
            print("No solar data found for the provided location.")

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")

# Example usage
if __name__ == "__main__":
    latitude = 39.7392  # Example latitude (Denver, CO)
    longitude = -104.9903  # Example longitude (Denver, CO)
    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"  # Replace with your actual API key
    output_file = "solar_data.csv"  # Specify the output CSV file name

    get_solar_data(latitude, longitude, api_key, output_file)
