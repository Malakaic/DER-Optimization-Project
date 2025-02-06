import os
import requests
import pandas as pd
import numpy as np

def main():
    # Definitions for API key:
    #longitude = -86.87
    #latitude = 48
    wind_data_type = "windspeed_100m"
    year = 2023
    user_email = "malakaicrane@gmail.com"
    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"

    # Set the folder path for "Environmental Data"
    folder_name = "Environmental Data"
    project_dir = os.getcwd()
    folder_path = os.path.join(project_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Define file paths
    wind_speed_file = os.path.join(folder_path, "wind_data.csv")
    output_file = os.path.join(folder_path, "wind_power_output.csv")

    # Download the CSV data
    download_wind_csv(long, lat, wind_data_type, year, user_email, api_key, wind_speed_file)

    turbine_capacity = 1500  # kW
    turbine_efficiency = 35  # percentage
    rotor_diameter = 77  # meters

    # Calculate wind power from CSV
    calculate_wind_power_with_columns(wind_speed_file, output_file, turbine_capacity, turbine_efficiency, rotor_diameter)

def download_wind_csv(lon, lat, wind_data_type, year, user_email, api_key, wind_speed_file):
    """
    Downloads CSV data from the given API URL and saves it to the 'Environmental Data' folder.
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

def calculate_wind_power_with_columns(wind_speed_file, output_file, turbine_capacity, turbine_efficiency, rotor_diameter):
    """
    Reads wind speed data from a CSV file, calculates power output, and saves it to another CSV file with the required columns.
    """
    try:
        # Read CSV, skipping irrelevant rows
        df = pd.read_csv(wind_speed_file, skiprows=2)

        # Verify necessary columns are present
        required_columns = ['Year', 'Month', 'Day', 'Hour', 'Minute']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"The column '{col}' is missing from the data.")

        # Extract the wind speed column
        wind_speed_column = next((col for col in df.columns if "wind speed" in col.lower()), None)
        if not wind_speed_column:
            raise ValueError("Wind speed column not found in the data.")
        df['wind_speed'] = df[wind_speed_column]

        # Calculate power output (in kW) for each wind speed before adjustments
        air_density = 1.225  # kg/m^3 (standard air density at sea level)
        swept_area = np.pi * (rotor_diameter / 2) ** 2  # m^2
        df['power_raw'] = 0.5 * air_density * swept_area * (df['wind_speed'] ** 3) * turbine_efficiency / 1000  # kW

        # Apply turbine capacity limit
        df['power_output'] = df['power_raw'].apply(lambda x: min(x, turbine_capacity))

        # Select and reorder columns for output
        output_columns = required_columns + ['wind_speed', 'power_raw', 'power_output']
        df[output_columns].to_csv(output_file, index=False)

        print(f"Detailed wind power output saved to: {output_file}")

        # Calculate total power output
        total_power_kwh = df['power_output'].sum()
        print(f"Total wind power produced: {total_power_kwh:.2f} kWh")
        return total_power_kwh
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
