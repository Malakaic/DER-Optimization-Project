import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import config
from Menu_Bar import MenuBar
from Objectives import Objective_Menu
from DERs import Der_menu_page
from Calculate import Calculate_Button
from Load_Inputs import LoadDemandSection
from Location_Input import Location

class EnergyResourceApp(tk.Tk):
    def __init__(self, master):
        self.master = master
        self.master.title("Energy Resource Optimization")

        # Make master window expandable
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Create a frame to hold everything
        self.container = ttk.Frame(self.master)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Configure resizing of container
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create a Canvas for scrolling
        self.canvas = tk.Canvas(self.container)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Add a horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure canvas to use the scrollbar
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)

        # Create a frame inside the canvas
        self.main_frame = ttk.Frame(self.canvas)
        self.window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Allow resizing of main_frame
        self.main_frame.bind("<Configure>", self.update_scroll_region)

        # Create the menu bar
        self.menu = MenuBar(master)

        # Left frame for location & load demand
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Ensure left frame rows resize properly
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)

        # Right frame for objectives & DERs
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Add sections
        self.location_page = Location(self.master)
        self.location_page.create_location_section(self.left_frame)

        self.load_page = LoadDemandSection(self.master)
        self.load_page.create_load_demand_section(self.left_frame)

        self.objective_page = Objective_Menu(self.master)
        self.objective_page.create_weighted_objectives_section(self.right_frame)

        self.der_page = Der_menu_page(self.master)
        self.der_page.create_der_section(self.right_frame)

        # Calculate button
        self.calculate_button = Calculate_Button(self.master, self.location_page)
        self.calculate_button = tk.Button(self.main_frame, text="Calculate", command=self.calculate_button.calculate)
        self.calculate_button.config(font=('Helvetica', 14, 'bold'), bg='black', fg='white')
        self.calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Bind the close event to a custom method
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_scroll_region(self, event):
        """Update the scrolling region to include the full size of the content."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_closing(self):
        """Handle the window close event."""
        self.master.quit()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyResourceApp(root)
    root.mainloop()
