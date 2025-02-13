import csv
import os
import tkinter as tk
import requests
from tkinter import filedialog, ttk 


class Objective_Menu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
    def create_weighted_objectives_section(self, frame):
            """Creates a weighted objectives section."""
            objectives_frame = ttk.LabelFrame(frame, text="Weighted Objectives")
            objectives_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

            tk.Label(objectives_frame, text="Financial:").grid(row=0, column=0, padx=5)
            self.financial_entry = tk.Entry(objectives_frame)
            self.financial_entry.grid(row=0, column=1, padx=5)

            tk.Label(objectives_frame, text="Efficiency:").grid(row=1, column=0, padx=5)
            self.efficiency_obj_entry = tk.Entry(objectives_frame)
            self.efficiency_obj_entry.grid(row=1, column=1, padx=5)

            tk.Label(objectives_frame, text="Sustainability:").grid(row=2, column=0, padx=5)
            self.sustainability_entry = tk.Entry(objectives_frame)
            self.sustainability_entry.grid(row=2, column=1, padx=5)

            objectives_frame.grid_rowconfigure(0, weight=1)
            objectives_frame.grid_rowconfigure(1, weight=1)
            objectives_frame.grid_rowconfigure(2, weight=1)