import os
import requests
import pandas as pd
import numpy as np

def main():
    # Definitions for API key:
    lon = -86.908
    lat = 40.426
    solar_data_type = "solar_irradiance"
    year = 2023
    user_email = "malakaicrane@gmail.com"
    api_key = "YT5auN6kF3hMbh7c1bQeyKCZYssN2DH0sv3zmZpG"

    # Set the folder path for "Environmental Data"
    folder_name = "Environmental Data"
    project_dir = os.getcwd()
    folder_path = os.path.join(project_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Define file paths
    solar_data_file = os.path.join(folder_path, "solar_data_2.csv")
    output_file = os.path.join(folder_path, "solar_power_output.csv")

    # Download the CSV data
    download_solar_csv(lon, lat, solar_data_type, year, user_email, api_key, solar_data_file)

    panel_capacity = 400  # kW
    panel_efficiency = 20  # percentage
    panel_area = 1.6 * 1  # m^2 per panel (example size)

    # Calculate solar power from CSV
    #calculate_solar_power_with_columns(solar_data_file, output_file, panel_capacity, panel_efficiency, panel_area)

def download_solar_csv(lon, lat, solar_data_type, year, user_email, api_key, solar_data_file):
    """
    Downloads CSV data from the given API URL and saves it to the 'Environmental Data' folder.
    """
    api_url = f"https://developer.nrel.gov/api/pvwatts/v8.csv?api_key={api_key}&lat={lat}&lon={lon}&system_capacity=1&module_type=0&losses=10&array_type=1&tilt=20&azimuth=180&dataset=nsrdb&timeframe=hourly&email={user_email}"
    
    try:
        response = requests.get(api_url)
        
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

if __name__ == "__main__":
    main()


""""
def calculate_solar_power_with_columns(solar_data_file, output_file, panel_capacity, panel_efficiency, panel_area):
    
    # Reads solar irradiance data from a CSV file, calculates power output, and saves it to another CSV file with the required columns.
    
    try:
        # Read CSV, skipping irrelevant rows
        df = pd.read_csv(solar_data_file, skiprows=29)

        # Verify necessary columns are present
        required_columns = ['month', 'day', 'hour']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"The column '{col}' is missing from the data.")

        # Extract the solar irradiance column
        solar_irradiance_column = next((col for col in df.columns if "irradiance" in col.lower()), None)
        if not solar_irradiance_column:
            raise ValueError("Solar irradiance column not found in the data.")
        df['solar_irradiance'] = df[solar_irradiance_column]

        # Calculate power output (in kW) for each solar irradiance value before adjustments
        df['power_raw'] = df['solar_irradiance'] * panel_area * panel_efficiency / 1000  # kW

        # Apply panel capacity limit
        df['power_output'] = df['power_raw'].apply(lambda x: min(x, panel_capacity))

        # Select and reorder columns for output
        output_columns = required_columns + ['solar_irradiance', 'power_raw', 'power_output']
        df[output_columns].to_csv(output_file, index=False)

        print(f"Detailed solar power output saved to: {output_file}")

        # Calculate total power output
        total_power_kwh = df['power_output'].sum()
        print(f"Total solar power produced: {total_power_kwh:.2f} kWh")
        return total_power_kwh
    
    except Exception as e:
        print(f"An error occurred: {e}")
"""