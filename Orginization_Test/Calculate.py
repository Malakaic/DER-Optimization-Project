import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests



class Calculate_Button(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
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
