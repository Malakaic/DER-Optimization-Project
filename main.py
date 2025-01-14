import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests

# Other parts of your class remain unchanged...

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
        """Creates a DER entry section."""
        der_frame = ttk.LabelFrame(frame, text="Distributed Energy Resources (DER)")
        der_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create treeview for DER entries
        self.der_tree = ttk.Treeview(der_frame, columns=("Name", "Type", "Cost", "Capacity", "Efficiency"), show='headings')
        self.der_tree.heading("Name", text="Name")
        self.der_tree.heading("Type", text="Type")
        self.der_tree.heading("Cost", text="Cost ($/kWh)")
        self.der_tree.heading("Capacity", text="Capacity (kW)")
        self.der_tree.heading("Efficiency", text="Efficiency (%)")

        # Scale the columns
        self.der_tree.column("Name", width=150)
        self.der_tree.column("Type", width=100)
        self.der_tree.column("Cost", width=100)
        self.der_tree.column("Capacity", width=100)
        self.der_tree.column("Efficiency", width=100)

        self.der_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create scrollbars
        self.scrollbar_y = ttk.Scrollbar(der_frame, orient="vertical", command=self.der_tree.yview)
        self.der_tree.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.grid(row=1, column=1, sticky="ns")

        self.scrollbar_x = ttk.Scrollbar(der_frame, orient="horizontal", command=self.der_tree.xview)
        self.der_tree.configure(xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_x.grid(row=2, column=0, sticky="ew")

        # Create DER input fields above the tree
        self.create_der_input_fields(der_frame)

        # Add Remove button
        self.remove_button = tk.Button(der_frame, text="Remove Selected DER", command=self.remove_selected_der)
        self.remove_button.grid(row=0, column=2, padx=5)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyResourceApp(root)
    root.mainloop()
