import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
from Inputs import InputPage




class Calculate_Button(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.location = InputPage(parent)
        self.location.create_location_section(parent)
    
    def gather_input_data(self):
        """Retrieve user input data"""
            
        city = self.location.get_city.get()
        state = self.location.get_state.get()
        country = self.location.get_country.get()
        return city, state, country

    def get_coordinates(self, city, state, country):
        """Retrieve coordinates for the given city, state, and country."""
        global latitude, longitude  #Declare global variables
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
                return latitude,longitude
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
    
        latitude, longitude = self.get_coordinates(city, state, country)

        if latitude and longitude:
            # Open results window to display the coordinates
            self.open_results_window(f"Latitude: {latitude}\nLongitude: {longitude}")
        else:
            self.open_results_window("Error", "Could not retrieve coordinates.")

    def open_results_window(self, message):
        """Open a new window to display the calculation results."""
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")

        results_frame = ttk.Frame(results_window)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(results_frame, text="Calculation Results", font=('Helvetica', 16)).pack(pady=10)

        # Display latitude and longitude
        tk.Label(results_frame, text=message).pack(anchor='w')
          

   


