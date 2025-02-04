import time
print("Starting script...")

start_time = time.time()
import Retrive_coordinates_V3
print(f"Retrive_coordinates_V3 imported in {time.time() - start_time:.2f} seconds")

start_time = time.time()
import Get_Wind_V2
print(f"Get_Wind_V2 imported in {time.time() - start_time:.2f} seconds")

start_time = time.time()
import GUI_Wind_test
print(f"GUI Wind Test imported in {time.time() - start_time:.2f} seconds")

latitude = None
longitude = None

def main(city, state, country):

    global latitude, longitude

    print("GUI Starting up")
    latitude, longitude = Retrive_coordinates_V3.get_coordinates(city, state, country)

    # Check if coordinates were retrieved successfully
    if latitude is not None and longitude is not None:
        print(f"Coordinates for {city}, {state}, {country}: Latitude: {latitude}, Longitude: {longitude}")

        # Call the function to get wind data using the coordinates
        Get_Wind_V2.wind_function(latitude, longitude)
    else:
        print("Could not retrieve coordinates.")


if __name__ == "__main__":
    print("Launching GUI...")
    start_time = time.time()
    GUI_Wind_test.create_gui()
    print(f"GUI launched in {time.time() - start_time:.2f} seconds")
