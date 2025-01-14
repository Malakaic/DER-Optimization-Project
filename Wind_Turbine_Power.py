import requests
import csv
import pandas as pd
import numpy as np

def main():
    # Definitions for API key:
    lon = -86.87
    lat = 48
    wind_data_type = "windspeed_100m"
    year = 2023
    user_email = "malakaicrane@gmail.com"
    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"

    # Output CSV file
    wind_speed_file = "wind_data.csv"
    
    # Download the CSV data
    download_wind_csv(lon, lat, wind_data_type, year, user_email, api_key, wind_speed_file)

    turbine_capacity = 1500 # kW
    turbine_efficiency = 35 # percentage
    rotor_diameter = 77 # meters

    power_output_file = "wind_power_output.csv"

    calculate_wind_power_from_csv(wind_speed_file, power_output_file, turbine_capacity, turbine_efficiency, rotor_diameter)



def download_wind_csv(lon, lat, wind_data_type, year, user_email, api_key, wind_speed_file):
    """
    Downloads CSV data from the given API URL and saves it to a local file.
    """
    api_url = f"https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-bchrrr-v1-0-0-download.csv?wkt=POINT({lon} {lat})&attributes={wind_data_type}&names={year}&utc=false&leap_day=true&email={user_email}&api_key={api_key}"
    
    try:
        response = requests.get(api_url)
        
        # Check if the response is successful
        if response.status_code == 200:
            with open(wind_speed_file, 'wb') as file:
                file.write(response.content)
            print(f"Data successfully downloaded and saved to {wind_speed_file}")
        else:
            print(f"Failed to download data. HTTP Status Code: {response.status_code}")
            print(f"Error Details: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


def calculate_wind_power_from_csv(wind_speed_file, power_output_file, turbine_capacity, turbine_efficiency, rotor_diameter):
    
    try:
        # Read CSV, skipping irrelevant rows
        df = pd.read_csv(wind_speed_file, skiprows=2)
        
        # Extract the wind speed column
        wind_speed_column = next(col for col in df.columns if "wind speed" in col.lower())
        df['wind_speed'] = df[wind_speed_column]

        # Calculate power output (in kW) for each wind speed before adjustments
        air_density = 1.225  # kg/m^3 (standard air density at sea level)
        swept_area = np.pi * (rotor_diameter / 2) ** 2  # m^2
        df['power_raw'] = 0.5 * air_density * swept_area * (df['wind_speed'] ** 3) * turbine_efficiency / 1000  # kW
        
        # Apply turbine capacity limit
        df['power'] = df['power_raw'].apply(lambda x: min(x, turbine_capacity))
        
        # Write to output CSV
        output_columns = ['wind_speed', 'power_raw', 'power']
        df[output_columns].to_csv(power_output_file, index=False)
        
        print(f"Detailed wind power output saved to: {power_output_file}")

        # Calculate total power output
        total_power_kwh = df['power'].sum()
        print(f"Total wind power produced: {total_power_kwh:.2f} kWh")
        return total_power_kwh
    
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()