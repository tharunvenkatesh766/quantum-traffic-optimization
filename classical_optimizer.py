def classical_traffic_optimizer(traffic_data):
    """
    Classical traffic optimization.

    Selects the intersections with the highest
    traffic pressure.
    """

    pressure_list = []

    for intersection, data in traffic_data.items():

        vehicles = data["vehicles"]
        queue = data["queue"]
        capacity = data["capacity"]

        congestion = (vehicles + queue) / capacity

        pressure = (
            vehicles
            + queue
            + congestion * 50
        )

        pressure_list.append(
            (intersection, pressure)
        )

    # Sort from highest pressure to lowest pressure
    pressure_list.sort(
        key=lambda x: x[1],
        reverse=True
    )

    # Select approximately half of the intersections
    number_to_select = max(
        2,
        len(traffic_data) // 2
    )

    selected = pressure_list[:number_to_select]

    selected_intersections = [
        item[0]
        for item in selected
    ]

    print("\n==============================================")
    print(" CLASSICAL TRAFFIC OPTIMIZATION")
    print("==============================================")

    print("\nClassical selected intersections:")

    for intersection, pressure in selected:
        print(
            f"{intersection} -> SELECTED "
            f"(Pressure: {pressure:.2f})"
        )

    return selected_intersections