import requests
import json
import csv
import os

def get_pvwatts_hourly_data(api_key, address, system_capacity, azimuth, tilt, losses, array_type, module_type, dc_ac_ratio, inv_eff, gcr, dataset, radius, soiling, albedo, bifaciality):
    """
    Fetch hourly solar production data from the NREL PVWatts API and save it as a CSV file.
    """
    # Base URL for the PVWatts API
    base_url = "https://developer.nrel.gov/api/pvwatts/v8.json"
    
    # API request parameters
    params = {
        "api_key": api_key,
        "address": address,
        "system_capacity": system_capacity,
        "azimuth": azimuth,
        "tilt": tilt,
        "losses": losses,
        "array_type": array_type,
        "module_type": module_type,
        "dc_ac_ratio": dc_ac_ratio,
        "inv_eff": inv_eff,
        "gcr": gcr,
        "dataset": dataset,
        "radius": radius,
        "soiling": soiling,
        "albedo": albedo,
        "bifaciality": bifaciality,
        "timeframe": "hourly"  # Request hourly data
    }

    # Send the API request
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract hourly AC output
        if "outputs" in data:
            hourly_ac_output = data["outputs"]["ac"]

            # Check if hourly data is present
            if hourly_ac_output:
                # Create the folder if it doesn't exist
                folder_name = "Environmental Data"
                os.makedirs(folder_name, exist_ok=True)

                # File path for the CSV
                file_path = os.path.join(folder_name, "solar_data.csv")

                # Write data to the CSV file
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write header
                    writer.writerow(["Hour", "Solar Power Output (kWh)"])

                    # Write hourly data
                    for hour, power_output in enumerate(hourly_ac_output, start=1):
                        writer.writerow([hour, power_output])

                print(f"Hourly solar data saved to {file_path}")
            else:
                print("Error: No hourly output data found in the response.")
        else:
            print("Error: No output data found in the response.")
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        print("Response text:", response.text)

# Example usage
api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"  # Replace with your actual API key
address = "west lafayette, in"
system_capacity = 10  # System capacity in kW
azimuth = 180  # Azimuth angle in degrees
tilt = 10  # Tilt angle in degrees
losses = 14  # System losses as a percentage
array_type = 1  # Fixed array type
module_type = 0  # Module type
dc_ac_ratio = 1.2  # DC to AC ratio
inv_eff = 96.0  # Inverter efficiency in percentage
gcr = 0.4  # Ground coverage ratio
dataset = "nsrdb"  # Dataset to use
radius = 0  # Radius for dataset lookup
soiling = "12|4|45|23|9|99|67|12.54|54|9|0|7.6"  # Monthly soiling losses
albedo = 0.3  # Albedo value
bifaciality = 0.7  # Bifaciality factor

get_pvwatts_hourly_data(api_key, address, system_capacity, azimuth, tilt, losses, array_type, module_type, dc_ac_ratio, inv_eff, gcr, dataset, radius, soiling, albedo, bifaciality)
