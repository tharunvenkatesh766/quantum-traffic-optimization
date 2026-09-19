# ============================================================
# EMERGENCY VEHICLE DETECTION
# ============================================================


def detect_emergency(vehicle):

    vehicle_type = vehicle.get(
        "type",
        ""
    ).lower()

    emergency_types = [
        "ambulance",
        "fire_truck",
        "police"
    ]

    if vehicle_type in emergency_types:

        return True

    return False


def get_emergency_priority(vehicle):

    if not detect_emergency(vehicle):

        return 0

    vehicle_type = vehicle.get(
        "type",
        ""
    ).lower()

    if vehicle_type == "ambulance":

        return 3

    elif vehicle_type == "fire_truck":

        return 2

    elif vehicle_type == "police":

        return 1

    return 0


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    vehicle = {
        "id": "AMB001",
        "type": "ambulance"
    }

    if detect_emergency(vehicle):

        print(
            "Emergency vehicle detected!"
        )

        print(
            "Vehicle:",
            vehicle["id"]
        )

        print(
            "Type:",
            vehicle["type"]
        )

        print(
            "Priority:",
            get_emergency_priority(vehicle)
        )

    else:

        print(
            "Normal vehicle"
        )