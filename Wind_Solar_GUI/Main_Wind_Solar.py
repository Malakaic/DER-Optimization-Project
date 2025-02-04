import time
print("Starting script...")

start_time = time.time()
import Retrieve_Coordinates_Wind_Solar
print(f"Retrive coordinates imported in {time.time() - start_time:.2f} seconds")

start_time = time.time()
import Wind_Power_Wind_Solar
print(f"Wind Power imported in {time.time() - start_time:.2f} seconds")

start_time = time.time()
import Solar_PV_Power_Wind_Solar
print(f"Solar PV Power imported in {time.time() - start_time:.2f} seconds")

start_time = time.time()
import Embedded_GUI_Wind_Solar
print(f"GUI imported in {time.time() - start_time:.2f} seconds")

#latitude = None
#longitude = None

def main(city, state, country):

    #global latitude, longitude

    print("GUI Starting up")
    lat_2, lon_2 = Retrieve_Coordinates_Wind_Solar.get_coordinates_wind_solar(city, state, country)

    # Check if coordinates were retrieved successfully
    if lat_2 is not None and lon_2 is not None:
        print(f"Coordinates for {city}, {state}, {country}: Latitude: {lat_2}, Longitude: {lon_2}")

        # Call the function to get wind data using the coordinates
        Wind_Power_Wind_Solar.wind_function_wind_solar(lat_2, lon_2)
        Solar_PV_Power_Wind_Solar.solar_function(lat_2, lon_2)
    else:
        print("Could not retrieve coordinates.")


if __name__ == "__main__":
    print("Launching GUI...")
    start_time = time.time()
    Embedded_GUI_Wind_Solar.create_gui()
    print(f"GUI launched in {time.time() - start_time:.2f} seconds")
