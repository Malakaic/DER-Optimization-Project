from Retrive_coordinates import get_coordinates

def store_and_print_coordinates(city, state, country):
    """Retrieve, store, and print latitude and longitude."""
    latitude, longitude = get_coordinates(city, state, country)

    if latitude is not None and longitude is not None:
        print(f"Stored Coordinates:\nLatitude: {latitude}\nLongitude: {longitude}")
    else:
        print("Could not retrieve coordinates.")

if __name__ == "__main__":
    city = input("Enter city: ")
    state = input("Enter state: ")
    country = input("Enter country: ")

    store_and_print_coordinates(city, state, country)
