import PySAM.Battery as Battery

def calculate_storage_capacity_new_class(battery_power_kw, battery_energy_kwh, roundtrip_efficiency=90):
    """
    Calculates the usable storage capacity and energy throughput of a battery system using PySAM.

    Parameters:
        battery_power_kw (float): Maximum power rating of the battery in kW.
        battery_energy_kwh (float): Total energy capacity of the battery in kWh.
        roundtrip_efficiency (float): Round-trip efficiency of the battery as a percentage (default is 90%).

    Returns:
        dict: A dictionary containing the following:
            - usable_energy_kwh (float): Usable energy capacity in kWh.
            - max_discharge_kw (float): Maximum discharge power in kW.
            - max_charge_kw (float): Maximum charge power in kW.
    """
    # Create a custom instance of the Battery class
    battery = Battery.new()

    # Set battery parameters
    battery.batt_power_charge_max_kw = battery_power_kw  # Max charge power (kW)
    battery.batt_power_discharge_max_kw = battery_power_kw  # Max discharge power (kW)
    battery.batt_energy_nominal = battery_energy_kwh  # Total energy capacity (kWh)
    battery.batt_efficiency = roundtrip_efficiency / 100  # Efficiency as a decimal

    # Perform calculations
    usable_energy_kwh = battery.batt_energy_nominal * battery.batt_efficiency
    max_discharge_kw = battery.batt_power_discharge_max_kw
    max_charge_kw = battery.batt_power_charge_max_kw

    return {
        "usable_energy_kwh": usable_energy_kwh,
        "max_discharge_kw": max_discharge_kw,
        "max_charge_kw": max_charge_kw
    }

# Example usage
if __name__ == "__main__":
    battery_data = {
        "battery_power_kw": 50,  # kW
        "battery_energy_kwh": 200,  # kWh
        "roundtrip_efficiency": 90  # Percentage
    }
    
    result = calculate_storage_capacity_new_class(
        battery_power_kw=battery_data["battery_power_kw"],
        battery_energy_kwh=battery_data["battery_energy_kwh"],
        roundtrip_efficiency=battery_data["roundtrip_efficiency"]
    )
    
    print("Battery Storage Capacity Results:")
    print(f"Usable Energy: {result['usable_energy_kwh']} kWh")
    print(f"Max Discharge Power: {result['max_discharge_kw']} kW")
    print(f"Max Charge Power: {result['max_charge_kw']} kW")
