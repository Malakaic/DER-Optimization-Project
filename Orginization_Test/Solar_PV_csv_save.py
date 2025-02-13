import os
import requests
import pandas as pd
import numpy as np
import json

cache = {}

def solar_function(self, latitude, longitude):
    # API Parameter Definitions

        # Check if latitude and longitude are valid
    if not (isinstance(latitude, (int, float)) and isinstance(longitude, (int, float))):
        raise ValueError("Latitude and longitude must be numeric.")

    # Cache key
    cache_key = f"{latitude},{longitude}"

    #address = "west lafayette, in"
    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"
    lat = latitude
    lon = longitude
    system_capacity = 10  # System capacity in kW - Required
    azimuth = 180  # Azimuth angle in degrees - Required
    tilt = 20  # Tilt angle in degrees - Required
    losses = 10  # System losses as a percentage - Required
    array_type = 1  # Fixed array type - Required (0 = fixed - open rack, 1 = fixed - roof mount, 2 = 1-axis, 3 = 1-axis backtracking, 4 = 2-axis )
    module_type = 0  # Module type - Required (0 = standard, 1 = premium, 2 = thin film)
    dataset = "nsrdb"  # Dataset to use - TMY data


    # Set the folder path for "Environmental Data"
    folder_name = "Environmental Data V4"
    project_dir = os.getcwd()
    folder_path = os.path.join(project_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Define file paths
    solar_data_file = os.path.join(folder_path, "solar_data_saved.csv")
    #output_file = os.path.join(folder_path, "solar_power_output.csv")

    # Download the CSV data
    if not os.path.exists(solar_data_file):
        download_solar_csv(api_key, lat, lon, system_capacity, azimuth, tilt, losses, array_type, module_type, dataset, solar_data_file)


    # Calculate solar power from CSV
    #calculate_solar_power_with_columns(solar_data_file, output_file, panel_capacity, panel_efficiency, panel_area)

def download_solar_csv(api_key, lat, lon, system_capacity, azimuth, tilt, losses, array_type, module_type, dataset, solar_data_file):
    """
    Downloads CSV data from the given API URL and saves it to the 'Environmental Data' folder.
    """
    api_url = f"https://developer.nrel.gov/api/pvwatts/v8.csv"

        # API request parameters
    params = {
        "api_key": api_key,
        "lat": lat,
        "lon": lon,
        "system_capacity": system_capacity,
        "azimuth": azimuth,
        "tilt": tilt,
        "losses": losses,
        "array_type": array_type,
        "module_type": module_type,
        "dataset": dataset,
        "timeframe": "hourly"  # Request hourly data
    }
    

    try:
        response = requests.get(api_url, params=params)
        
        # Check if the response is successful
        if response.status_code == 200:
            with open(solar_data_file, 'wb') as file:
                file.write(response.content)
            print(f"Data successfully downloaded and saved to {solar_data_file}")
        else:
            print(f"Failed to download data. HTTP Status Code: {response.status_code}")
            print(f"Error Details: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

