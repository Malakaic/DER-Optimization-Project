import os
import pandas as pd

def main():
    """
    Main function to execute the battery performance calculations.
    """
    # Battery specifications
    battery_specs = {
        'nominal_voltage': 3.7,  # Voltage per battery in volts
        'capacity_ah': 100,      # Capacity per battery in ampere-hours
        'efficiency': 0.95,      # Battery efficiency (95%)
        'cost_per_kwh': 150      # Cost per kWh in dollars
    }
    
    # System specifications for 24 hours
    hours = 24
    system_specs = {
        'load': [10, 12, 9, 8, 7, 6, 5, 8, 10, 12, 11, 13, 15, 14, 13, 12, 11, 9, 8, 7, 6, 7, 8, 9],  # Load demand in kW
        'solar_pv': [0, 0, 0, 0, 1, 3, 5, 7, 10, 12, 14, 16, 14, 12, 10, 8, 6, 4, 2, 0, 0, 0, 0, 0],  # Solar PV output in kW
        'wind_turbine': [3, 4, 5, 6, 5, 4, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 4, 3, 2]     # Wind turbine output in kW
    }
    
    # Calculate performance
    results_df = calculate_battery_performance(battery_specs, system_specs, hours)
    
    # Save results to a CSV file
    save_results_to_csv(results_df)

def calculate_battery_performance(battery_specs, system_specs, hours, max_batteries=10, step=2):
    """
    Calculate battery performance over 24 hours for a range of configurations.
    
    Args:
    - battery_specs: Dictionary with battery specifications.
    - system_specs: Dictionary with load, solar PV, and wind turbine values over 24 hours.
    - hours: Number of hours to simulate (e.g., 24 for a full day).
    - max_batteries: Maximum number of batteries in series or parallel.
    
    Returns:
    - DataFrame with results for all configurations.
    """
    results = []

    for series_count in range(2, max_batteries + 1, step):
        for parallel_count in range(2, max_batteries + 1, step):
            total_voltage = battery_specs['nominal_voltage'] * series_count
            total_capacity_ah = battery_specs['capacity_ah'] * parallel_count
            total_capacity_kwh = (total_voltage * total_capacity_ah * battery_specs['efficiency']) / 1000
            
            # Calculate cost per configuration
            total_cost = total_capacity_kwh * battery_specs['cost_per_kwh']
            
            for hour in range(hours):
                effective_load = system_specs['load'][hour] - (
                    system_specs['solar_pv'][hour] + system_specs['wind_turbine'][hour]
                )
                effective_load = max(effective_load, 0)  # Ensure load can't be negative
                
                # Calculate length of discharge
                if effective_load > 0:
                    length_of_discharge = total_capacity_kwh / effective_load
                else:
                    length_of_discharge = 0  # Set to 0 when effective load is 0
                
                results.append({
                    'Hour': hour + 1,
                    'Series': series_count,
                    'Parallel': parallel_count,
                    'Total Capacity (kWh)': total_capacity_kwh,
                    'Effective Load (kW)': effective_load,
                    'Length of Discharge (hours)': length_of_discharge,
                    'Total Cost ($)': total_cost  # Cost is fixed for each configuration
                })
    
    return pd.DataFrame(results)

def save_results_to_csv(results_df, folder_name="environmental data", filename="battery_performance_results.csv"):
    """
    Save the results to a CSV file in a specified folder.
    
    Args:
    - results_df: DataFrame with the results.
    - folder_name: Name of the folder to save the file in.
    - filename: Name of the output CSV file.
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Define the file path
    file_path = os.path.join(folder_name, filename)
    
    # Save the DataFrame to the CSV file
    results_df.to_csv(file_path, index=False)
    print(f"Results saved to {file_path}")



# Execute the main function
if __name__ == "__main__":
    main()
