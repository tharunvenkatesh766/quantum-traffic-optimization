# ============================================================
# TRAFFIC PERFORMANCE METRICS
# Quantum-Enhanced Adaptive Traffic Optimization
# ============================================================


def calculate_traffic_metrics(
    traffic_data,
    signal_timing
):
    """
    Calculate traffic performance metrics.

    Metrics:
    - Total vehicles
    - Total queue length
    - Average waiting time
    - Total throughput
    - Average congestion
    - Estimated fuel consumption
    - Estimated CO2 emissions
    """

    # ========================================================
    # INITIAL VALUES
    # ========================================================

    total_vehicles = 0
    total_queue = 0
    total_capacity = 0

    total_waiting_time = 0
    total_throughput = 0

    intersection_count = len(
        traffic_data
    )

    # ========================================================
    # PROCESS EACH INTERSECTION
    # ========================================================

    for intersection, data in traffic_data.items():

        vehicles = data["vehicles"]
        queue = data["queue"]
        capacity = data["capacity"]

        green_time = signal_timing[
            intersection
        ]["green_time"]

        # ====================================================
        # WAITING TIME
        # ====================================================
        #
        # Simulation assumption:
        # Queue vehicles contribute 2 minutes
        # Vehicles contribute 0.5 minutes.
        #
        # This is an estimated simulation metric,
        # not real-world measured waiting time.
        # ====================================================

        waiting_time = (
            (queue * 2)
            +
            (vehicles * 0.5)
        )

        total_waiting_time += (
            waiting_time
        )

        # ====================================================
        # THROUGHPUT
        # ====================================================
        #
        # Estimated vehicles processed based on:
        #
        # capacity × green-time ratio
        #
        # Limited by the number of vehicles.
        # ====================================================

        capacity_throughput = (
            capacity
            * (green_time / 60)
        )

        throughput = min(
            vehicles,
            capacity_throughput
        )

        total_throughput += (
            throughput
        )

        # ====================================================
        # TOTALS
        # ====================================================

        total_vehicles += vehicles

        total_queue += queue

        total_capacity += capacity

    # ========================================================
    # AVERAGE WAITING TIME
    # ========================================================

    if intersection_count > 0:

        average_waiting_time = (
            total_waiting_time
            / intersection_count
        )

    else:

        average_waiting_time = 0

    # ========================================================
    # AVERAGE CONGESTION
    # ========================================================

    if total_capacity > 0:

        average_congestion = (
            total_queue
            / total_capacity
        )

    else:

        average_congestion = 0

    # ========================================================
    # ESTIMATED FUEL CONSUMPTION
    # ========================================================
    #
    # Simulation assumption:
    # 0.08 litres per waiting-time unit.
    #
    # This is an estimated value for the prototype.
    # ========================================================

    fuel_consumption = (
        total_waiting_time
        * 0.08
    )

    # ========================================================
    # ESTIMATED CO2 EMISSIONS
    # ========================================================
    #
    # Approximate emission factor:
    # 2.31 kg CO2 per litre of petrol.
    #
    # This is a simulation estimate.
    # ========================================================

    co2_emissions = (
        fuel_consumption
        * 2.31
    )

    # ========================================================
    # RETURN ALL METRICS
    # ========================================================

    return {

        "total_vehicles":
            total_vehicles,

        "total_queue":
            total_queue,

        "average_waiting_time":
            average_waiting_time,

        "total_throughput":
            total_throughput,

        "average_congestion":
            average_congestion,

        "fuel_consumption":
            fuel_consumption,

        "co2_emissions":
            co2_emissions
    }


# ============================================================
# DISPLAY METRICS
# ============================================================

def display_traffic_metrics(metrics):
    """
    Display traffic performance metrics neatly.
    """

    print()
    print("==============================================")
    print(" TRAFFIC PERFORMANCE METRICS")
    print("==============================================")

    print()

    print(
        f"Total vehicles: "
        f"{metrics['total_vehicles']}"
    )

    print(
        f"Total queue length: "
        f"{metrics['total_queue']}"
    )

    print(
        f"Average waiting time: "
        f"{metrics['average_waiting_time']:.2f} units"
    )

    print(
        f"Total throughput: "
        f"{metrics['total_throughput']:.2f} vehicles"
    )

    print(
        f"Average congestion: "
        f"{metrics['average_congestion']:.2%}"
    )

    print(
        f"Estimated fuel consumption: "
        f"{metrics['fuel_consumption']:.2f} litres"
    )

    print(
        f"Estimated CO2 emissions: "
        f"{metrics['co2_emissions']:.2f} kg"
    )

    print()
    print("==============================================")