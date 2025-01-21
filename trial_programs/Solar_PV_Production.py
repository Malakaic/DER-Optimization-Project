import requests
import json

#OLD CODE
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
    
def calculate_solar_panel_production(latitude, longitude, api_key, panel_capacity_kW, panel_area_m2, panel_efficiency):
    """Calculate expected solar panel production using GHI."""
    # Get solar resource data
    solar_data = get_solar_data(latitude, longitude, api_key)
    
    if solar_data is None:
        print("No solar data available.")
        return

    # Extract average GHI for calculations
    annual_avg_ghi = solar_data['annual_avg_ghi']
    monthly_avg_ghi = solar_data['monthly_avg_ghi']

    # Calculate expected yearly production
    # Based on capacity
    yearly_production_capacity = panel_capacity_kW * annual_avg_ghi * panel_efficiency * 365  # kWh

    # Based on size
    yearly_production_area = panel_area_m2 * panel_efficiency * annual_avg_ghi * 365  # kWh

    # Calculate monthly production based on average GHI
    monthly_production_capacity = {month: (panel_capacity_kW * ghi * panel_efficiency * 30) for month, ghi in monthly_avg_ghi.items()}
    monthly_production_area = {month: (panel_area_m2 * panel_efficiency * ghi * 30) for month, ghi in monthly_avg_ghi.items()}

    print("Expected Yearly Production (kWh) based on Capacity:", yearly_production_capacity)
    print("Expected Yearly Production (kWh) based on Area:", yearly_production_area)
    print("Expected Monthly Production (kWh) based on Capacity:")
    for month, production in monthly_production_capacity.items():
        print(f"{month.capitalize()}: {production:.2f}")
    
    print("Expected Monthly Production (kWh) based on Area:")
    for month, production in monthly_production_area.items():
        print(f"{month.capitalize()}: {production:.2f}")

# Example usage
latitude = 40.4167
longitude = -86.8753
api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"  # Replace with your actual API key
panel_capacity_kW = 5.0  # Example panel capacity in kW
panel_area_m2 = 20.0  # Example panel area in m²
panel_efficiency = 0.8  # Example panel efficiency (15%)

calculate_solar_panel_production(latitude, longitude, api_key, panel_capacity_kW, panel_area_m2, panel_efficiency)

