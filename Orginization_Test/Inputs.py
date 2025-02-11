import csv
import os
import tkinter as tk
import requests
from tkinter import filedialog, ttk



class InputPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def create_location_section(self,frame):
        """Creates a location section for data inputs."""


        location_frame = ttk.LabelFrame(frame, text="Location")
        location_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        tk.Label(location_frame, text="City:").grid(row=0, column=0, padx=5)
        self.city_entry = tk.Entry(location_frame)
        self.city_entry.grid(row=0, column=1, padx=5)

        tk.Label(location_frame, text="State:").grid(row=0, column=2, padx=5)
        self.state_entry = tk.Entry(location_frame)
        self.state_entry.grid(row=0, column=3, padx=5)

        tk.Label(location_frame, text="Country:").grid(row=1, column=0, padx=5)
        self.country_entry = tk.Entry(location_frame)
        self.country_entry.grid(row=1, column=1, padx=5)

        location_frame.grid_rowconfigure(0, weight=1)
        location_frame.grid_rowconfigure(1, weight=1)

    def create_load_demand_section(self, frame):
            """Creates a load demand section."""
            load_frame = ttk.LabelFrame(frame, text="Load Demand")
            load_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

            self.load_choice = tk.StringVar(value="CSV Entry")
            csv_radiobutton = tk.Radiobutton(load_frame, text="CSV Entry", variable=self.load_choice, value="CSV Entry", command=self.toggle_load_input)
            csv_radiobutton.grid(row=0, column=0)

            manual_radiobutton = tk.Radiobutton(load_frame, text="Manual Entry", variable=self.load_choice, value="Manual Entry", command=self.toggle_load_input)
            manual_radiobutton.grid(row=0, column=1)

            self.csv_entry = tk.Entry(load_frame, state="disabled")
            self.csv_entry.grid(row=1, column=0, padx=5)

            self.csv_button = tk.Button(load_frame, text="Browse", command=self.browse_csv, state="disabled")
            self.csv_button.grid(row=1, column=1)

            # Monthly entries
            self.monthly_entries = {}
            for i, month in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], start=2):
                tk.Label(load_frame, text=f"{month}:").grid(row=i, column=0, padx=5)
                entry = tk.Entry(load_frame)
                entry.grid(row=i, column=1, padx=5)
                self.monthly_entries[month] = entry

            # Create a new grid rate input section below monthly entries
            tk.Label(load_frame, text="Grid Rate ($/kWh):").grid(row=14, column=0, padx=5, pady=(10, 0))
            self.grid_rate_entry = tk.Entry(load_frame)
            self.grid_rate_entry.grid(row=14, column=1, padx=5)

            load_frame.grid_rowconfigure(0, weight=1)
            load_frame.grid_rowconfigure(1, weight=1)

    def toggle_load_input(self):
        """Toggle visibility of CSV entry based on load choice."""
        if self.load_choice.get() == "CSV Entry":
            self.csv_entry.config(state="normal")
            self.csv_button.config(state="normal")
            for entry in self.monthly_entries.values():
                entry.config(state="disabled")
        else:
            self.csv_entry.config(state="disabled")
            self.csv_button.config(state="disabled")
            for entry in self.monthly_entries.values():
                entry.config(state="normal")

    def browse_csv(self):
        """Open a file dialog to browse for a CSV file."""
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.csv_entry.config(state="normal")
            self.csv_entry.delete(0, tk.END)
            self.csv_entry.insert(0, filename)
            self.csv_entry.config(state="disabled")

    def get_city(self):
        return self.city_entry.get()

    def get_state(self):
        return self.state_entry.get()

    def get_country(self):
        return self.country_entry.get()