import requests
import json

def get_solar_data(latitude, longitude, api_key):
    """Fetch solar resource data from the NREL Solar Resource API."""
    url = f"https://developer.nrel.gov/api/solar/solar_resource/v1.json?api_key={api_key}&lat={latitude}&lon={longitude}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("Solar Resource API Response:", json.dumps(data, indent=4))  # Pretty print the response
        
        # Check if there are errors in the response
        if 'errors' in data and data['errors']:
            print("Error in API response:", data['errors'])
            return None
        
        # Extract annual values
        annual_avg_dni = data['outputs']['avg_dni']['annual']
        annual_avg_ghi = data['outputs']['avg_ghi']['annual']
        annual_avg_lat_tilt = data['outputs']['avg_lat_tilt']['annual']
        
        # Extract monthly values
        monthly_avg_dni = data['outputs']['avg_dni']['monthly']
        monthly_avg_ghi = data['outputs']['avg_ghi']['monthly']
        monthly_avg_lat_tilt = data['outputs']['avg_lat_tilt']['monthly']

        # Create a structured output
        solar_data = {
            "annual_avg_dni": annual_avg_dni,
            "annual_avg_ghi": annual_avg_ghi,
            "annual_avg_lat_tilt": annual_avg_lat_tilt,
            "monthly_avg_dni": monthly_avg_dni,
            "monthly_avg_ghi": monthly_avg_ghi,
            "monthly_avg_lat_tilt": monthly_avg_lat_tilt
        }

        return solar_data
    else:
        print(f"An error occurred: {response.status_code} - {response.text}")
        return None
    
def calculate_solar_panel_production(latitude, longitude, api_key, panel_efficiency=0.15, panel_area=1.6):
    """Calculate expected solar panel production using the PVWatts API."""
    # Get solar resource data
    solar_data = get_solar_data(latitude, longitude, api_key)
    
    if solar_data is None:
        print("No solar data available.")
        return

    # Extract average GHI for calculations
    annual_avg_ghi = solar_data['annual_avg_ghi']
    monthly_avg_ghi = solar_data['monthly_avg_ghi']

    # Calculate expected yearly production
    yearly_production = annual_avg_ghi * panel_efficiency * panel_area * 365  # kWh

    # Calculate monthly production based on average GHI
    monthly_production = {month: (ghi * panel_efficiency * panel_area * 30) for month, ghi in monthly_avg_ghi.items()}

    print("Expected Yearly Production (kWh):", yearly_production)
    print("Expected Monthly Production (kWh):")
    for month, production in monthly_production.items():
        print(f"{month.capitalize()}: {production:.2f}")

# Example usage
latitude = 40
longitude = -105
api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"  # Replace with your actual API key
calculate_solar_panel_production(latitude, longitude, api_key)
