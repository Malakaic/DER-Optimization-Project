import requests
import json

#OLD CODE
def get_pvwatts_data(api_key, address, system_capacity, azimuth, tilt, losses, array_type, module_type, dc_ac_ratio, inv_eff, gcr, dataset, radius, soiling, albedo, bifaciality):
    """
    Fetch solar production data from the NREL PVWatts API.
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
        "bifaciality": bifaciality
    }

    # Send the API request
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print("API Response:", json.dumps(data, indent=4))  # Print the response for debugging

        # Extract relevant data
        if "outputs" in data:
            ac_annual = data["outputs"]["ac_annual"]
            ac_monthly = data["outputs"]["ac_monthly"]

            print("\nAnnual Solar Production (kWh):", ac_annual)
            print("Monthly Solar Production (kWh):")
            for i, month_output in enumerate(ac_monthly, start=1):
                print(f"Month {i}: {month_output} kWh")
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

get_pvwatts_data(api_key, address, system_capacity, azimuth, tilt, losses, array_type, module_type, dc_ac_ratio, inv_eff, gcr, dataset, radius, soiling, albedo, bifaciality)
