import Retrive_coordinates_V2
import Get_Wind

latitude = None
longitude = None

def main():

    global latitude, longitude


    city = input("Enter city: ")
    state = input("Enter state: ")
    country = input("Enter country: ")

    latitude, longitude = Retrive_coordinates_V2.get_coordinates(city, state, country)

    # Call the function to get wind data using the coordinates
    Get_Wind.wind_function(latitude, longitude)
    
    # Check if coordinates were retrieved successfully
    if latitude is not None and longitude is not None:
        print(f"Coordinates for {city}, {state}, {country}: Latitude: {latitude}, Longitude: {longitude}")

    else:
        print("Could not retrieve coordinates.")


if __name__ == "__main__":
    main()