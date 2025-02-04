import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests

# Other parts of your class remain unchanged...

 # Initialize PV-related variables
pv_counter = 1  # Start from 1 or 0 based on your preference
pv_data_dict = {}  # Dictionary to store PV data
wind_counter = 1  # Start from 1 or 0 based on your preference
wind_data_dict = {}  # Dictionary to store Wind data
battery_counter = 1  # Start from 1 or 0 based on your preference
battery_data_dict = {}  # Dictionary to store Battery data

def browse_csv(self):
    """Open a file dialog to browse for a CSV file."""
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filename:
        self.csv_entry.config(state="normal")
        self.csv_entry.delete(0, tk.END)
        self.csv_entry.insert(0, filename)
        self.csv_entry.config(state="disabled")
        self.load_csv(filename)

def load_csv(self, filename):
    """Load data from the selected CSV file into the input fields."""
    try:
        with open(filename, mode='r') as csvfile:
            reader = csv.reader(csvfile)
            # Read the grid rate and monthly entries from the CSV
            grid_rate = next(reader)[0]  # Assuming the first row has grid rate
            self.grid_rate_entry.delete(0, tk.END)
            self.grid_rate_entry.insert(0, grid_rate)

            for month, entry in zip(["January", "February", "March", "April", "May", "June",
                                     "July", "August", "September", "October", "November", "December"], reader):
                self.monthly_entries[month].delete(0, tk.END)
                self.monthly_entries[month].insert(0, entry[0])  # Assuming single value for each month

            # Handle DER entries (if present in the CSV)
            for row in reader:
                if row:
                    self.der_tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", f"Error opening file: {e}")

# DER GUI Class
class EnergyResourceApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Energy Resource Optimization")

        # Create the main frame
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the menu bar
        self.create_menu()

        # Create the left side frame
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create the right side frame
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configure grid weights for scaling
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(3, weight=1)

        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(2, weight=1)
        self.right_frame.grid_columnconfigure(3, weight=1)

        # Create the location section
        self.create_location_section(self.left_frame)

        # Create the load demand section
        self.create_load_demand_section(self.left_frame)

        # Create the weighted objectives section
        self.create_weighted_objectives_section(self.right_frame)

        # Create the DER section
        self.create_der_section(self.right_frame)

        # Create the calculate button
        self.calculate_button = tk.Button(self.main_frame, text="Calculate", command=self.calculate)
        self.calculate_button.config(font=('Helvetica', 14, 'bold'), bg='black', fg='white')
        self.calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

    def create_menu(self):
        """Creates the menu bar for file operations."""
        menu_bar = tk.Menu(self.master)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save as CSV", command=self.save_to_csv)
        file_menu.add_command(label="Open CSV", command=self.open_csv)
        file_menu.add_command(label="Clear All", command=self.clear_all)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.master.config(menu=menu_bar)

    # Save to CSV file function
    def save_to_csv(self):
        """Save current entries to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write location data
                    writer.writerow(["City", self.city_entry.get()])
                    writer.writerow(["State", self.state_entry.get()])
                    writer.writerow(["Country", self.country_entry.get()])

                    # Write load demand data
                    writer.writerow(["Load Choice", self.load_choice.get()])
                    if self.load_choice.get() == "CSV Entry":
                        writer.writerow(["CSV File Path", self.csv_entry.get()])
                    else:
                        for month, entry in self.monthly_entries.items():
                            writer.writerow([month, entry.get()])
                    writer.writerow(["Grid Rate", self.grid_rate_entry.get()])

                    # Write weighted objectives data
                    writer.writerow(["Financial", self.financial_entry.get()])
                    writer.writerow(["Efficiency", self.efficiency_obj_entry.get()])
                    writer.writerow(["Sustainability", self.sustainability_entry.get()])

                    # Write DER entries
                    writer.writerow(["Name", "Type", "Cost", "Capacity", "Efficiency"])
                    for child in self.der_tree.get_children():
                        writer.writerow(self.der_tree.item(child)["values"])

                messagebox.showinfo("Success", "Data saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")

    # open CSV file function
    def open_csv(self):
        """Open a CSV file and load the data into the app."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[0] == "City":
                            self.city_entry.delete(0, tk.END)
                            self.city_entry.insert(0, row[1])
                        elif row[0] == "State":
                            self.state_entry.delete(0, tk.END)
                            self.state_entry.insert(0, row[1])
                        elif row[0] == "Country":
                            self.country_entry.delete(0, tk.END)
                            self.country_entry.insert(0, row[1])
                        elif row[0] == "Grid Rate":
                            self.grid_rate_entry.delete(0, tk.END)
                            self.grid_rate_entry.insert(0, row[1])
                        elif row[0] == "CSV File Path":
                            self.csv_entry.config(state="normal")
                            self.csv_entry.delete(0, tk.END)
                            self.csv_entry.insert(0, row[1])
                            self.csv_entry.config(state="disabled")
                        elif row[0] in ["Financial", "Efficiency", "Sustainability"]:
                            if row[0] == "Financial":
                                self.financial_entry.delete(0, tk.END)
                                self.financial_entry.insert(0, row[1])
                            elif row[0] == "Efficiency":
                                self.efficiency_obj_entry.delete(0, tk.END)
                                self.efficiency_obj_entry.insert(0, row[1])
                            elif row[0] == "Sustainability":
                                self.sustainability_entry.delete(0, tk.END)
                                self.sustainability_entry.insert(0, row[1])
                        elif row[0] in self.monthly_entries.keys():
                            # Correctly populate the monthly entries
                            self.monthly_entries[row[0]].delete(0, tk.END)
                            self.monthly_entries[row[0]].insert(0, row[1])
                        elif row[0] == "Name":
                            continue  # Skip the header for DER
                        else:
                            self.der_tree.insert("", "end", values=row)

                messagebox.showinfo("Success", "Data loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {e}")

    def clear_all(self):
        """Clear all input fields."""
        self.city_entry.delete(0, tk.END)
        self.state_entry.delete(0, tk.END)
        self.country_entry.delete(0, tk.END)
        self.grid_rate_entry.delete(0, tk.END)
        self.csv_entry.delete(0, tk.END)
        self.financial_entry.delete(0, tk.END)
        self.efficiency_obj_entry.delete(0, tk.END)
        self.sustainability_entry.delete(0, tk.END)
        for entry in self.monthly_entries.values():
            entry.delete(0, tk.END)
        self.der_tree.delete(*self.der_tree.get_children())

    def create_location_section(self, frame):
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

                        global pv_counter,pv_data_dict

                        # Create a list with the data for the current PV
                        pv_data = [
                            pv_name_entry.get(),  # Name
                            cost_entry.get(),     # System capital cost
                            min_pv_entry.get(),   # Min PV size
                            max_pv_entry.get()    # Max PV size
                        ]

                        # Check if a save with the same name already exists
                        existing_key = None
                        for key, value in pv_data_dict.items():
                            if value[0] == pv_data[0]:  # Compare the "Name" field
                                existing_key = key

                        if existing_key is not None:
                            # Overwrite the existing save
                            # Show a message box indicating the overwrite
                            overwrite = messagebox.askyesno("Overwrite Entry", f"An entry with the name '{pv_data[0]}' already exists. Do you want to overwrite it?")
                            if overwrite:
                                # Overwrite the existing save
                                pv_data_dict[existing_key] = pv_data
                            else:
                                # Prompt user to change the name
                                messagebox.showinfo("Change Name", "Please change the name of the PV before saving.")
                        else:
                            #Save Current Data
                            pv_data_dict[pv_counter] = pv_data
                            # Increment the counter for the next save
                            pv_counter += 1

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

                        global wind_counter,wind_data_dict

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
                        for key, value in wind_data_dict.items():
                            if value[0] == wind_data[0]:  # Compare the "Name" field
                                existing_key = key

                        if existing_key is not None:
                            # Overwrite the existing save
                            # Show a message box indicating the overwrite
                            overwrite = messagebox.askyesno("Overwrite Entry", f"An entry with the name '{wind_data[0]}' already exists. Do you want to overwrite it?")
                            if overwrite:
                                # Overwrite the existing save
                                wind_data_dict[existing_key] = wind_data
                            else:
                                # Prompt user to change the name
                                messagebox.showinfo("Change Name", "Please change the name of the wind turbine before saving.")
                        else:
                            #Save Current Data
                            wind_data_dict[wind_counter] = wind_data
                            # Increment the counter for the next save
                            wind_counter += 1
                            
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
                        global battery_counter,battery_data_dict

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
                        for key, value in battery_data_dict.items():
                            if value[0] == battery_data[0]:
                                existing_key = key

                        if existing_key is not None:
                            # Overwrite the existing save
                            # Show a message box indicating the overwrite
                            overwrite = messagebox.askyesno("Overwrite Entry", f"An entry with the name '{battery_data[0]}' already exists. Do you want to overwrite it?")
                            if overwrite:
                                # Overwrite the existing save
                                battery_data_dict[existing_key] = battery_data
                            else:
                                # Prompt user to change the name
                                messagebox.showinfo("Change Name", "Please change the name of the battery before saving.")
                        else:
                            #Save Current Data
                            battery_data_dict[battery_counter] = battery_data
                            # Increment the counter for the next save
                            battery_counter += 1

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

    """" calculate results section """

    def gather_input_data(self):
        """Retrieve user input data"""
        
        city = self.city_entry.get()
        state = self.state_entry.get()
        country = self.country_entry.get()
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
            'format': 'json'\
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


if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyResourceApp(root)
    root.mainloop()
