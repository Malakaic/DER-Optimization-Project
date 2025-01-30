import Retrive_coordinates_V3
import Get_Wind_V2

latitude = None
longitude = None

def main(city, state, country):

    global latitude, longitude



    latitude, longitude = Retrive_coordinates_V3.get_coordinates(city, state, country)

    # Call the function to get wind data using the coordinates
    Get_Wind_V2.wind_function(latitude, longitude)
    
    # Check if coordinates were retrieved successfully
    if latitude is not None and longitude is not None:
        print(f"Coordinates for {city}, {state}, {country}: Latitude: {latitude}, Longitude: {longitude}")

    else:
        print("Could not retrieve coordinates.")


if __name__ == "__main__":
    import GUI_Wind_test