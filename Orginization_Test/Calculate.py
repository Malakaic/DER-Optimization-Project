import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import Wind_csv_save
import Solar_PV_csv_save
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from Inputs import InputPage

# Example usage
configurations = [
    {'solar': 5, 'solar_panels': 20, 'wind': 10, 'wind_turbines': 4, 'battery': 20, 'battery_units': 10, 'inverter': 5, 'inverters': 1, 'price': 10000},
    {'solar': 8, 'solar_panels': 32, 'wind': 12, 'wind_turbines': 5, 'battery': 25, 'battery_units': 12, 'inverter': 7, 'inverters': 1, 'price': 15000},
    {'solar': 10, 'solar_panels': 40, 'wind': 15, 'wind_turbines': 6, 'battery': 30, 'battery_units': 15, 'inverter': 10, 'inverters': 2, 'price': 20000},
    {'solar': 12, 'solar_panels': 48, 'wind': 18, 'wind_turbines': 7, 'battery': 35, 'battery_units': 18, 'inverter': 12, 'inverters': 2, 'price': 25000}
]

class Calculate_Button(tk.Frame):
    def __init__(self, parent,location_page):
        super().__init__(parent)
        self.parent = parent
        self.location_page =  location_page
      #  self.location.create_location_section(parent)
    
    def gather_input_data(self):
        """Retrieve user input data"""
        
        #Declare Global Variables
       # global city, state, country

        city = self.location_page.city_entry.get()
        state = self.location_page.state_entry.get()
        country = self.location_page.country_entry.get()

        return city, state, country

    def get_coordinates(self, city, state, country):
        """Retrieve coordinates for the given city, state, and country."""
        # LocationIQ API key (insert your API key here)
        self.api_key = "pk.06116c260378fbaf82bb1d519c2e0e2d"
        self.base_url = "https://us1.locationiq.com/v1/search.php"

        location_str = f"{city}, {state}, {country}"

        params = {
            'key': self.api_key,
            'q': location_str,
            'format': 'json'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            data = response.json()
            if data:
                # Get the latitude and longitude from the response
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                return float(latitude),float(longitude)
            else:
                return None, None
        except requests.exceptions.RequestException as e:
            return None, None

    def calculate(self):
        """Perform calculations, print results, and open results window."""

        city, state, country = self.gather_input_data()

        if not city or not state or not country:
            self.open_results_window("Error", "Please enter a valid city, state, and country.")
            return
       # global latitude, longitude
        latitude, longitude = self.get_coordinates(city, state, country)

        if latitude is not None and longitude is not None:
            try:
                print ("pulling wind data")
                Wind_csv_save.wind_function_main(self, latitude, longitude)
                print ("pulling solar data")
                Solar_PV_csv_save.solar_function(self, latitude, longitude)
                self.open_results_window(f"Latitude: {latitude}\nLongitude: {longitude}", configurations)
            except ValueError as e:
                self.open_results_window(f"Error: {e}")
        else:
            self.open_results_window("Error", "Could not retrieve coordinates.")

    '''
    def open_results_window(self, message):
        """Open a new window to display the calculation results."""
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")

        results_frame = ttk.Frame(results_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(results_frame, text="Calculation Results", font=('Helvetica', 16)).pack(pady=10)

        # Display latitude and longitude
        tk.Label(results_frame, text=message).pack(anchor='w')
    '''

    def open_results_window(self, message, configurations):
        """Open a new window to display the calculation results."""
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")

        results_frame = ttk.Frame(results_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(results_frame, text="Calculation Results", font=('Helvetica', 16)).pack(pady=10)

        # Display latitude and longitude
        tk.Label(results_frame, text=message).pack(anchor='w')

        # Display configurations
        for i, config in enumerate(configurations, start=1):
            config_frame = ttk.Frame(results_frame)
            config_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            tk.Label(config_frame, text=f"Configuration {i}", font=('Helvetica', 14, 'bold')).pack(anchor='w')
       
            tk.Label(config_frame, text=f"Solar: {config['solar']} kW ({config['solar_panels']} panels)").pack(anchor='w')
            tk.Label(config_frame, text=f"Wind: {config['wind']} kW ({config['wind_turbines']} turbines)").pack(anchor='w')
            tk.Label(config_frame, text=f"Battery: {config['battery']} kWh ({config['battery_units']} units)").pack(anchor='w')
            tk.Label(config_frame, text=f"Inverter: {config['inverter']} kW ({config['inverters']} units)").pack(anchor='w')
            tk.Label(config_frame, text=f"Price: ${config['price']}").pack(anchor='w')

          

   


