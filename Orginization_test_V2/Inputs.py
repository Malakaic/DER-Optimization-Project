import csv
import os
import tkinter as tk
import requests
from tkinter import filedialog, ttk
import Menu_Bar
#from Calculate import Calculate_Button



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


#    def get_city(self):
 #       return self.city_entry.get()

  #  def get_state(self):
   #     return self.state_entry.get()

    #def get_country(self):
     #   return self.country_entry.get()