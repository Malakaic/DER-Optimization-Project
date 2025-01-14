import tkinter as tk
from tkinter import ttk
""" pip install geopy
    pip install requests
"""
import requests

class LocationCoordinates:
    def __init__(self, master):
        self.master = master
        self.master.title("Location Coordinates Finder")

        # LocationIQ API key (insert your API key here)
        self.api_key = "pk.06116c260378fbaf82bb1d519c2e0e2d"
        self.base_url = "https://us1.locationiq.com/v1/search.php"

        # Labels and Entries for user input
        self.city_label = tk.Label(master, text="City:")
        self.city_label.grid(row=0, column=0)
        self.city_entry = tk.Entry(master)
        self.city_entry.grid(row=0, column=1)

        self.state_label = tk.Label(master, text="State:")
        self.state_label.grid(row=1, column=0)
        self.state_entry = tk.Entry(master)
        self.state_entry.grid(row=1, column=1)

        self.country_label = tk.Label(master, text="Country:")
        self.country_label.grid(row=2, column=0)
        self.country_entry = tk.Entry(master)
        self.country_entry.grid(row=2, column=1)

        # Button to get coordinates
        self.get_coordinates_button = tk.Button(master, text="Get Coordinates", command=self.get_coordinates)
        self.get_coordinates_button.grid(row=3, column=0, columnspan=2)

        # Label to display results
        self.result_label = tk.Label(master, text="", font=('Helvetica', 14))
        self.result_label.grid(row=4, column=0, columnspan=2)

    def get_coordinates(self):
        """Retrieve coordinates for the given city, state, and country."""
        city = self.city_entry.get()
        state = self.state_entry.get()
        country = self.country_entry.get()

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
                self.result_label.config(text=f"Coordinates: {latitude}, {longitude}")
            else:
                self.result_label.config(text="Location not found.")
        except requests.exceptions.RequestException as e:
            self.result_label.config(text=f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LocationCoordinates(root)
    root.mainloop()
