# config.py
#This is where all global variables will be stored, access these variables by importing this file at the top of your code, and using config.(variable_name) to access the variable.

 # Initialize PV-related variables
pv_counter = 1  # Start from 1 or 0 based on your preference
pv_data_dict = {}  # Dictionary to store PV data (name, capacity, lifespan, efficiency, module type, cost)
wind_counter = 1  # Start from 1 or 0 based on your preference
wind_data_dict = {}  # Dictionary to store Wind data (name, capacity, lifespan, efficiency, hub height, rotor diameter, cost)
battery_counter = 1  # Start from 1 or 0 based on your preference
battery_data_dict = {}  # Dictionary to store Battery data

# Initialize an empty list to store configurations
project_name = "Default_Project"  # Default project name


latitude = 0.0
longitude = 0.0

financial_weight = 25
efficiency_weight = 25
sustainability_weight = 25
power_quality_weight = 25