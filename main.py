# ============================================================
# QUANTUM-ENHANCED ADAPTIVE TRAFFIC SYSTEM
# ============================================================

from quntum.qubo_model import create_traffic_qubo
from quntum.quab_optimizer import get_quantum_solution
from quntum.classical_optimizer import classical_traffic_optimizer

from emergency.emergency_detection import (
    detect_emergency,
    get_emergency_priority
)

from emergency.green_corridor import (
    find_emergency_route,
    activate_green_corridor,
    calculate_route_cost
)

from metrics.traffic_metrics import (
    calculate_traffic_metrics,
    display_traffic_metrics
)


# ============================================================
# TRAFFIC DATA
# ============================================================

traffic_data = {

    "J1": {
        "vehicles": 80,
        "queue": 30,
        "capacity": 100
    },

    "J2": {
        "vehicles": 50,
        "queue": 15,
        "capacity": 100
    },

    "J3": {
        "vehicles": 20,
        "queue": 5,
        "capacity": 80
    },

    "J4": {
        "vehicles": 70,
        "queue": 25,
        "capacity": 100
    },

    "J5": {
        "vehicles": 60,
        "queue": 20,
        "capacity": 90
    },

    "J6": {
        "vehicles": 35,
        "queue": 10,
        "capacity": 80
    },

    "J7": {
        "vehicles": 90,
        "queue": 35,
        "capacity": 100
    },

    "J8": {
        "vehicles": 45,
        "queue": 15,
        "capacity": 90
    }
}


# ============================================================
# INTERSECTIONS
# ============================================================

intersections = list(
    traffic_data.keys()
)


# ============================================================
# DYNAMIC SIGNAL TIMING
# ============================================================

def calculate_signal_timing(
    traffic_data,
    intersections,
    quantum_selected
):

    signal_timing = {}

    for intersection in intersections:

        data = traffic_data[
            intersection
        ]

        vehicles = data["vehicles"]
        queue = data["queue"]
        capacity = data["capacity"]

        # ----------------------------------------------------
        # Congestion
        # ----------------------------------------------------

        congestion = (
            (vehicles + queue)
            / capacity
        )

        # ----------------------------------------------------
        # Traffic pressure
        # ----------------------------------------------------

        pressure = (
            vehicles
            + queue
            + (congestion * 50)
        )

        # ----------------------------------------------------
        # Base signal timing
        # ----------------------------------------------------

        if pressure >= 150:

            green_time = 60
            status = "CRITICAL TRAFFIC"

        elif pressure >= 100:

            green_time = 50
            status = "HIGH TRAFFIC"

        elif pressure >= 60:

            green_time = 40
            status = "MEDIUM TRAFFIC"

        else:

            green_time = 30
            status = "LOW TRAFFIC"

        # ----------------------------------------------------
        # Quantum priority
        # ----------------------------------------------------

        quantum_priority = (
            intersection
            in quantum_selected
        )

        if quantum_priority:

            green_time += 10

            if green_time > 70:

                green_time = 70

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        signal_timing[
            intersection
        ] = {

            "pressure": pressure,

            "congestion": congestion,

            "green_time": green_time,

            "status": status,

            "quantum_priority":
                quantum_priority
        }

    return signal_timing


# ============================================================
# MAIN PROGRAM
# ============================================================

print()

print("=============================================")
print(" QUANTUM-ENHANCED ADAPTIVE TRAFFIC SYSTEM")
print("=============================================")


# ============================================================
# STEP 1: CREATE TRAFFIC QUBO
# ============================================================

print()

print("STEP 1: CREATING TRAFFIC QUBO")

print()


intersections, Q, pressure = (
    create_traffic_qubo(
        traffic_data
    )
)


print()

print("Number of intersections:")
print(len(intersections))


print()

print("Intersections:")

for intersection in intersections:

    print(
        f"  {intersection}"
    )


# ============================================================
# TRAFFIC PRESSURE
# ============================================================

print()

print("Traffic pressure:")


for i, intersection in enumerate(
    intersections
):

    print(
        f"  {intersection} -> "
        f"{pressure[i]:.2f}"
    )


# ============================================================
# QUBO MATRIX
# ============================================================

print()

print("QUBO Matrix:")

print(Q)


# ============================================================
# STEP 2: QUANTUM OPTIMIZATION
# ============================================================

print()

print("==============================================")
print(" STEP 2: QUANTUM OPTIMIZATION")
print("==============================================")


quantum_selected = (
    get_quantum_solution(
        traffic_data
    )
)


# ============================================================
# STEP 2B: CLASSICAL OPTIMIZATION
# ============================================================

classical_selected = (
    classical_traffic_optimizer(
        traffic_data
    )
)


# ============================================================
# CLASSICAL VS QUANTUM
# ============================================================

print()

print("==============================================")
print(" CLASSICAL vs QUANTUM COMPARISON")
print("==============================================")


print()

print(
    "Classical selected intersections:"
)


for intersection in classical_selected:

    print(
        f"  {intersection}"
    )


print()

print(
    "Quantum selected intersections:"
)


for intersection in quantum_selected:

    print(
        f"  {intersection}"
    )


# ============================================================
# COMMON INTERSECTIONS
# ============================================================

common = (
    set(classical_selected)
    &
    set(quantum_selected)
)


print()

print(
    "Common intersections:"
)


if common:

    for intersection in sorted(
        common
    ):

        print(
            f"  {intersection}"
        )

else:

    print("  None")


# ============================================================
# CLASSICAL ONLY
# ============================================================

classical_only = (
    set(classical_selected)
    -
    set(quantum_selected)
)


print()

print(
    "Classical-only selections:"
)


if classical_only:

    for intersection in sorted(
        classical_only
    ):

        print(
            f"  {intersection}"
        )

else:

    print("  None")


# ============================================================
# QUANTUM ONLY
# ============================================================

quantum_only = (
    set(quantum_selected)
    -
    set(classical_selected)
)


print()

print(
    "Quantum-only selections:"
)


if quantum_only:

    for intersection in sorted(
        quantum_only
    ):

        print(
            f"  {intersection}"
        )

else:

    print("  None")


# ============================================================
# STEP 3: DYNAMIC SIGNAL TIMING
# ============================================================

print()

print("==============================================")
print(" STEP 3: DYNAMIC SIGNAL TIMING")
print("==============================================")


signal_timing = (
    calculate_signal_timing(
        traffic_data,
        intersections,
        quantum_selected
    )
)


for intersection in intersections:

    result = signal_timing[
        intersection
    ]

    pressure_value = result[
        "pressure"
    ]

    green_time = result[
        "green_time"
    ]

    status = result[
        "status"
    ]

    quantum_priority = result[
        "quantum_priority"
    ]

    print(
        f"{intersection} -> "
        f"Pressure: {pressure_value:.2f} | "
        f"Green: {green_time} sec | "
        f"{status}",
        end=""
    )

    if quantum_priority:

        print(
            " | QUANTUM PRIORITY"
        )

    else:

        print()


# ============================================================
# STEP 4: EMERGENCY VEHICLE DETECTION
# ============================================================

print()

print("==============================================")
print(" STEP 4: EMERGENCY VEHICLE DETECTION")
print("==============================================")


emergency_vehicle = {

    "id": "AMB001",

    "type": "ambulance"
}


is_emergency = detect_emergency(
    emergency_vehicle
)


priority = get_emergency_priority(
    emergency_vehicle
)


if is_emergency:

    print(
        "🚑 Emergency vehicle detected!"
    )

    print(
        f"Vehicle ID: "
        f"{emergency_vehicle['id']}"
    )

    print(
        f"Type: "
        f"{emergency_vehicle['type']}"
    )

    print(
        f"Priority: "
        f"{priority}"
    )

else:

    print(
        "No emergency vehicle detected."
    )


# ============================================================
# STEP 5: EMERGENCY GREEN CORRIDOR
# ============================================================

print()

print("==============================================")
print(" STEP 5: EMERGENCY GREEN CORRIDOR")
print("==============================================")


source = "J1"

destination = "J8"


# ------------------------------------------------------------
# Find emergency route
# ------------------------------------------------------------

emergency_route = (
    find_emergency_route(
        source,
        destination
    )
)


# ------------------------------------------------------------
# Validate route
# ------------------------------------------------------------

if not emergency_route:

    print(
        "No emergency route found."
    )

else:

    print()

    print(
        "Emergency route:"
    )

    print(
        " → ".join(
            emergency_route
        )
    )


# ============================================================
# ROUTE COST
# ============================================================

if emergency_route:

    route_cost = (
        calculate_route_cost(
            emergency_route
        )
    )

else:

    route_cost = 0


print()

print(
    f"Estimated route cost: "
    f"{route_cost}"
)


# ============================================================
# ACTIVATE GREEN CORRIDOR
# ============================================================

print()

print("======================================")
print(" EMERGENCY GREEN CORRIDOR")
print("======================================")


if emergency_route:

    print()

    print(
        "🚑 Emergency route:"
    )

    print(
        " → ".join(
            emergency_route
        )
    )

    print()

    print(
        "Traffic signal actions:"
    )

    for intersection in (
        emergency_route
    ):

        print(
            f"{intersection} -> "
            f"GREEN PRIORITY"
        )

    # --------------------------------------------------------
    # Activate corridor
    # --------------------------------------------------------

    activate_green_corridor(
        emergency_route
    )

else:

    print(
        "Emergency corridor could not "
        "be activated."
    )


# ============================================================
# STEP 6: TRAFFIC PERFORMANCE METRICS
# ============================================================

print()

print("==============================================")
print(" STEP 6: TRAFFIC PERFORMANCE METRICS")
print("==============================================")


metrics = calculate_traffic_metrics(
    traffic_data,
    signal_timing
)


display_traffic_metrics(
    metrics
)


# ============================================================
# FINAL TRAFFIC SYSTEM PLAN
# ============================================================

print()

print("==============================================")
print(" FINAL TRAFFIC SYSTEM PLAN")
print("==============================================")


# ============================================================
# QUANTUM SELECTION
# ============================================================

print()

print(
    "Quantum selected intersections:"
)


for intersection in quantum_selected:

    print(
        f"  {intersection} "
        f"-> QUANTUM SELECTED"
    )


# ============================================================
# CLASSICAL SELECTION
# ============================================================

print()

print(
    "Classical selected intersections:"
)


for intersection in classical_selected:

    print(
        f"  {intersection} "
        f"-> CLASSICAL SELECTED"
    )


# ============================================================
# FINAL SIGNAL TIMING
# ============================================================

print()

print(
    "Final signal timing:"
)


for intersection in intersections:

    result = signal_timing[
        intersection
    ]

    green_time = result[
        "green_time"
    ]

    status = result[
        "status"
    ]

    quantum_priority = result[
        "quantum_priority"
    ]

    print(
        f"  {intersection}: "
        f"{green_time} sec "
        f"({status})",
        end=""
    )

    if quantum_priority:

        print(
            " | QUANTUM PRIORITY"
        )

    else:

        print()


# ============================================================
# EMERGENCY PRIORITY
# ============================================================

print()

print(
    "🚑 Emergency priority:"
)


if emergency_route:

    for intersection in (
        emergency_route
    ):

        print(
            f"  {intersection} "
            f"-> GREEN PRIORITY"
        )

else:

    print(
        "  No emergency corridor"
    )


# ============================================================
# FINAL METRICS SUMMARY
# ============================================================

print()

print(
    "Traffic performance summary:"
)

print(
    f"  Vehicles: "
    f"{metrics['total_vehicles']}"
)

print(
    f"  Queue length: "
    f"{metrics['total_queue']}"
)

print(
    f"  Average waiting time: "
    f"{metrics['average_waiting_time']:.2f}"
)

print(
    f"  Throughput: "
    f"{metrics['total_throughput']:.2f}"
)

print(
    f"  Average congestion: "
    f"{metrics['average_congestion']:.2%}"
)

print(
    f"  Fuel consumption: "
    f"{metrics['fuel_consumption']:.2f} litres"
)

print(
    f"  CO2 emissions: "
    f"{metrics['co2_emissions']:.2f} kg"
)


# ============================================================
# SYSTEM EXECUTION COMPLETED
# ============================================================

print()

print("==============================================")
print(" SYSTEM EXECUTION COMPLETED")
print("==============================================")