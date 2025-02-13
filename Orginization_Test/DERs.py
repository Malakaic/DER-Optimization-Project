import csv
import os
import tkinter as tk
import requests
from tkinter import filedialog, messagebox, ttk
import config


class Der_menu_page (tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.pv_data_dict = config.pv_data_dict
        self.wind_data_dict = config.wind_data_dict
        self.battery_data_dict = config.battery_data_dict
        self.pv_counter = config.pv_counter
        self.wind_counter = config.wind_counter
        self.battery_counter = config.battery_counter
        
        
    def create_der_section(self, frame):

            der_frame = ttk.LabelFrame(frame, text="Select DER Resources")
            der_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

            # Define a dictionary to store the states of the checkboxes
            checkbox_states = {}

            # Define the options for the checkboxes
            options = ["PV", "Wind", "Battery", "Grids"]

            # Function to display the selected options
            def show_selected():

                # First, remove any previously created frames
                for child in frame.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.cget("text") in options:
                        child.destroy()

                selected = [option for option, var in checkbox_states.items() if var.get()]

                # Loop through each selected option and create a new frame for each
                for idx, option in enumerate(selected):
                    # Create a new frame for each selected option
                    result_frame = ttk.LabelFrame(frame, text=option)
                    result_frame.grid(row=2 + idx, column=0, sticky="nsew", padx=5, pady=5)

                    if option == "PV":
                        pv_frame = ttk.Frame(result_frame)  # A container for better layout
                        pv_frame.pack(pady=10, padx=10, fill="x")

                        # Text box for Name
                        pv_name_label = tk.Label(pv_frame, text="Name:", anchor="w")
                        pv_name_label.grid(row=0, column=0, sticky="w", padx=5)
                        pv_name_entry = tk.Entry(pv_frame)
                        pv_name_entry.grid(row=0, column=1, sticky="e", padx=5)

                        # Text box for System capital cost
                        cost_label = tk.Label(pv_frame, text="System capital cost ($/kW-DC):", anchor="w")
                        cost_label.grid(row=1, column=0, sticky="w", padx=5)
                        cost_entry = tk.Entry(pv_frame)
                        cost_entry.grid(row=1, column=1, sticky="e", padx=5)

                        # Text box for Minimum new PV size
                        min_pv_label = tk.Label(pv_frame, text="Minimum new PV size (kW-DC):", anchor="w")
                        min_pv_label.grid(row=2, column=0, sticky="w", padx=5)
                        min_pv_entry = tk.Entry(pv_frame)
                        min_pv_entry.grid(row=2, column=1, sticky="e", padx=5)

                        # Text box for Maximum new PV size
                        max_pv_label = tk.Label(pv_frame, text="Maximum new PV size (kW-DC):", anchor="w")
                        max_pv_label.grid(row=3, column=0, sticky="w", padx=5)
                        max_pv_entry = tk.Entry(pv_frame)
                        max_pv_entry.grid(row=3, column=1, sticky="e", padx=5)

                        # Save Button for PV
                        def save_pv_data():

                            # Create a list with the data for the current PV
                            pv_data = [
                                pv_name_entry.get(),  # Name
                                cost_entry.get(),     # System capital cost
                                min_pv_entry.get(),   # Min PV size
                                max_pv_entry.get()    # Max PV size
                            ]

                            # Check if a save with the same name already exists
                            existing_key = None
                            for key, value in config.pv_data_dict.items():
                                if value[0] == pv_data[0]:  # Compare the "Name" field
                                    existing_key = key

                            if existing_key is not None:
                                # Overwrite the existing save
                                # Show a message box indicating the overwrite
                                overwrite = messagebox.askyesno("Overwrite Entry", f"An entry with the name '{pv_data[0]}' already exists. Do you want to overwrite it?")
                                if overwrite:
                                    # Overwrite the existing save
                                    config.pv_data_dict[existing_key] = pv_data
                                    print(f"PV data with name '{pv_data[0]}' overwritten.")
                                else:
                                    # Prompt user to change the name
                                    messagebox.showinfo("Change Name", "Please change the name of the PV before saving.")
                            else:
                                #Save Current Data
                                config.pv_data_dict[config.pv_counter] = pv_data
                                print(f"PV data saved with name '{pv_data[0]}'.")
                                # Increment the counter for the next save
                                config.pv_counter += 1

                        pv_save_button = tk.Button(pv_frame, text="Save", command=save_pv_data)
                        pv_save_button.grid(row=6, column=0, columnspan=2, pady=10)

                    if option == "Wind":
                        # A container for the layout of all Wind-specific inputs
                        wind_frame = ttk.Frame(result_frame)
                        wind_frame.pack(pady=10, padx=10, fill="x")

                        # "Name" label and entry
                        wind_name_label = tk.Label(wind_frame, text="Name:", anchor="w")
                        wind_name_label.grid(row=0, column=0, sticky="w", padx=5)
                        wind_name_entry = tk.Entry(wind_frame)
                        wind_name_entry.grid(row=0, column=1, sticky="e", padx=5)

                        # "Size class" label and entry
                        size_class_label = tk.Label(wind_frame, text="Size class:", anchor="w")
                        size_class_label.grid(row=1, column=0, sticky="w", padx=5)
                        size_class_entry = tk.Entry(wind_frame)
                        size_class_entry.grid(row=1, column=1, sticky="e", padx=5)

                        # "System capital cost ($/kW)" label and entry
                        wind_cost_label = tk.Label(wind_frame, text="System capital cost ($/kW):", anchor="w")
                        wind_cost_label.grid(row=2, column=0, sticky="w", padx=5)
                        wind_cost_entry = tk.Entry(wind_frame)
                        wind_cost_entry.grid(row=2, column=1, sticky="e", padx=5)

                        # "Minimum size desired (kW AC)" label and entry
                        min_wind_size_label = tk.Label(wind_frame, text="Minimum size desired (kW AC):", anchor="w")
                        min_wind_size_label.grid(row=3, column=0, sticky="w", padx=5)
                        min_wind_size_entry = tk.Entry(wind_frame)
                        min_wind_size_entry.grid(row=3, column=1, sticky="e", padx=5)

                        # "Maximum size desired (kW AC)" label and entry
                        max_wind_size_label = tk.Label(wind_frame, text="Maximum size desired (kW AC):", anchor="w")
                        max_wind_size_label.grid(row=4, column=0, sticky="w", padx=5)
                        max_wind_size_entry = tk.Entry(wind_frame)
                        max_wind_size_entry.grid(row=4, column=1, sticky="e", padx=5)

                        # Save Button for Wind
                        def save_wind_data():

                            # Create a list with the data for the current turbine
                            wind_data = [
                                wind_name_entry.get(),   # Name
                                size_class_entry.get(),  # Size class entry
                                wind_cost_entry.get(),   # Wind cost entry
                                min_wind_size_entry.get(),  # Min wind size
                                max_wind_size_entry.get()   # Max wind size
                            ]

                            # Check if a save with the same name already exists
                            existing_key = None
                            for key, value in config.wind_data_dict.items():
                                if value[0] == wind_data[0]:  # Compare the "Name" field
                                    existing_key = key

                            if existing_key is not None:
                                # Overwrite the existing save
                                # Show a message box indicating the overwrite
                                overwrite = messagebox.askyesno("Overwrite Entry", f"An entry with the name '{wind_data[0]}' already exists. Do you want to overwrite it?")
                                if overwrite:
                                    # Overwrite the existing save
                                    config.wind_data_dict[existing_key] = wind_data
                                    print(f"Wind data with name '{wind_data[0]}' overwritten.")
                                else:
                                    # Prompt user to change the name
                                    messagebox.showinfo("Change Name", "Please change the name of the wind turbine before saving.")
                            else:
                                #Save Current Data
                                config.wind_data_dict[config.wind_counter] = wind_data
                                print(f"Wind data saved with name '{wind_data[0]}'.")
                                # Increment the counter for the next save
                                config.wind_counter += 1
                                
                        wind_save_button = tk.Button(wind_frame, text="Save", command=save_wind_data)
                        wind_save_button.grid(row=5, column=0, columnspan=2, pady=10)

                    if option == "Battery":
                        # A container for the layout of all Battery-specific inputs
                        battery_frame = ttk.Frame(result_frame)
                        battery_frame.pack(pady=10, padx=10, fill="x")

                        # "Name" label and entry
                        battery_name_label = tk.Label(battery_frame, text="Name:", anchor="w")
                        battery_name_label.grid(row=0, column=0, sticky="w", padx=5)
                        battery_name_entry = tk.Entry(battery_frame)
                        battery_name_entry.grid(row=0, column=1, sticky="e", padx=5)

                        # "Energy capacity cost ($/kWh)" label and entry
                        energy_cost_label = tk.Label(battery_frame, text="Energy capacity cost ($/kWh):", anchor="w")
                        energy_cost_label.grid(row=1, column=0, sticky="w", padx=5)
                        energy_cost_entry = tk.Entry(battery_frame)
                        energy_cost_entry.grid(row=1, column=1, sticky="e", padx=5)

                        # "Power capacity cost ($/kW)" label and entry
                        power_cost_label = tk.Label(battery_frame, text="Power capacity cost ($/kW):", anchor="w")
                        power_cost_label.grid(row=2, column=0, sticky="w", padx=5)
                        power_cost_entry = tk.Entry(battery_frame)
                        power_cost_entry.grid(row=2, column=1, sticky="e", padx=5)

                        # "Allow grid to charge battery" checkbox
                        grid_charge_var = tk.BooleanVar()
                        grid_charge_checkbox = tk.Checkbutton(
                            battery_frame, text="Allow grid to charge battery", variable=grid_charge_var, anchor="w"
                        )
                        grid_charge_checkbox.grid(row=3, column=0, columnspan=2, sticky="w", padx=5)

                        # "Minimum energy capacity (kWh)" label and entry
                        min_energy_label = tk.Label(battery_frame, text="Minimum energy capacity (kWh):", anchor="w")
                        min_energy_label.grid(row=4, column=0, sticky="w", padx=5)
                        min_energy_entry = tk.Entry(battery_frame)
                        min_energy_entry.grid(row=4, column=1, sticky="e", padx=5)

                        # "Maximum energy capacity (kWh)" label and entry
                        max_energy_label = tk.Label(battery_frame, text="Maximum energy capacity (kWh):", anchor="w")
                        max_energy_label.grid(row=5, column=0, sticky="w", padx=5)
                        max_energy_entry = tk.Entry(battery_frame)
                        max_energy_entry.grid(row=5, column=1, sticky="e", padx=5)

                        # Save Button for Battery
                        def save_battery_data():

                            # Create a list with the data for the current battery
                            battery_data = [
                                battery_name_entry.get(),
                                energy_cost_entry.get(),
                                power_cost_entry.get(),
                                grid_charge_var.get(),
                                min_energy_entry.get(),
                                max_energy_entry.get()
                            ]

                            # Check if a save with the same name already exists
                            existing_key = None
                            for key, value in config.battery_data_dict.items():
                                if value[0] == battery_data[0]:
                                    existing_key = key

                            if existing_key is not None:
                                # Overwrite the existing save
                                # Show a message box indicating the overwrite
                                overwrite = messagebox.askyesno("Overwrite Entry", f"An entry with the name '{battery_data[0]}' already exists. Do you want to overwrite it?")
                                if overwrite:
                                    # Overwrite the existing save
                                    config.battery_data_dict[existing_key] = battery_data
                                    print(f"Battery data with name '{battery_data[0]}' overwritten.")
                                else:
                                    # Prompt user to change the name
                                    messagebox.showinfo("Change Name", "Please change the name of the battery before saving.")
                            else:
                                #Save Current Data
                                config.battery_data_dict[config.battery_counter] = battery_data
                                print(f"Battery data saved with name '{battery_data[0]}'.")
                                # Increment the counter for the next save
                                config.battery_counter += 1

                        battery_save_button = tk.Button(battery_frame, text="Save", command=save_battery_data)
                        battery_save_button.grid(row=6, column=0, columnspan=2, pady=10)



            # Create checkboxes dynamically inside der_frame
            for option in options:
                var = tk.BooleanVar()  # Boolean variable for each checkbox
                checkbox_states[option] = var
                checkbox = tk.Checkbutton(der_frame, text=option, variable=var)
                checkbox.pack(anchor="w")  # Align checkboxes to the left

            # Create a button to confirm the selection inside der_frame
            confirm_button = tk.Button(der_frame, text="Confirm Selection", command=show_selected)
            confirm_button.pack(pady=10)

            # Label to display the selected options inside der_frame
            selection_label = tk.Label(der_frame, text="")
            selection_label.pack(pady=10)



    def create_der_input_fields(self, frame):
        """Creates input fields for DER entries."""
        der_input_frame = ttk.Frame(frame)
        der_input_frame.grid(row=0, column=0, padx=5, pady=5)

        tk.Label(der_input_frame, text="Name:").grid(row=0, column=0)
        self.der_name_entry = tk.Entry(der_input_frame)
        self.der_name_entry.grid(row=0, column=1)

        tk.Label(der_input_frame, text="Type:").grid(row=0, column=2)
        self.der_type_entry = ttk.Combobox(der_input_frame, values=["PV", "Wind Turbine", "Battery", "Converter"])
        self.der_type_entry.grid(row=0, column=3)

        tk.Label(der_input_frame, text="Cost ($/kWh):").grid(row=1, column=0)
        self.der_cost_entry = tk.Entry(der_input_frame)
        self.der_cost_entry.grid(row=1, column=1)

        tk.Label(der_input_frame, text="Capacity (kW):").grid(row=1, column=2)
        self.der_capacity_entry = tk.Entry(der_input_frame)
        self.der_capacity_entry.grid(row=1, column=3)

        tk.Label(der_input_frame, text="Efficiency (%):").grid(row=2, column=0)
        self.der_efficiency_entry = tk.Entry(der_input_frame)
        self.der_efficiency_entry.grid(row=2, column=1)

        self.add_der_button = tk.Button(der_input_frame, text="Add DER", command=self.add_der)
        self.add_der_button.grid(row=2, column=2, columnspan=2)

    def add_der(self):
        """Add a DER entry to the Treeview."""
        name = self.der_name_entry.get()
        type_ = self.der_type_entry.get()
        cost = self.der_cost_entry.get()
        capacity = self.der_capacity_entry.get()
        efficiency = self.der_efficiency_entry.get()

        if name and type_ and cost and capacity and efficiency:
            self.der_tree.insert("", "end", values=(name, type_, cost, capacity, efficiency))
            self.clear_der_entries()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    def remove_selected_der(self):
        """Remove the selected DER entry from the Treeview."""
        selected_item = self.der_tree.selection()
        if selected_item:
            self.der_tree.delete(selected_item)
        else:
            messagebox.showwarning("Selection Error", "Please select a DER entry to remove.")

    def clear_der_entries(self):
        """Clear DER input fields."""
        self.der_name_entry.delete(0, tk.END)
        self.der_type_entry.set('')  # Reset the dropdown
        self.der_cost_entry.delete(0, tk.END)
        self.der_capacity_entry.delete(0, tk.END)
        self.der_efficiency_entry.delete(0, tk.END)