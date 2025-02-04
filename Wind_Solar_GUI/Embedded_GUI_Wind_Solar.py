import tkinter as tk
from tkinter import messagebox
import Main_Wind_Solar  # Import the main file to call the main function

def submit_input():
    city = city_entry.get()
    state = state_entry.get()
    country = country_entry.get()

    if city and state and country:
        # Call the main function with user input
        Main_Wind_Solar.main(city, state, country)
    else:
        messagebox.showwarning("Input Error", "Please enter all fields.")

def create_gui():

    print ("create gui")
    # Create the main window
    root = tk.Tk()
    root.title("Location Input")

    # Create labels and entry fields
    tk.Label(root, text="City:").grid(row=0, column=0)
    tk.Label(root, text="State:").grid(row=1, column=0)
    tk.Label(root, text="Country:").grid(row=2, column=0)

    global city_entry, state_entry, country_entry
    city_entry = tk.Entry(root)
    state_entry = tk.Entry(root)
    country_entry = tk.Entry(root)

    city_entry.grid(row=0, column=1)
    state_entry.grid(row=1, column=1)
    country_entry.grid(row=2, column=1)

    # Create submit button
    submit_button = tk.Button(root, text="Submit", command=submit_input)
    submit_button.grid(row=3, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    print("gui file opened")
    create_gui()

