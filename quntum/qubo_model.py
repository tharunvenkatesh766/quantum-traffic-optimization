# ============================================================
# TRAFFIC QUBO MODEL
# Quantum-Enhanced Adaptive Urban Traffic Optimization
# ============================================================

import numpy as np


# ============================================================
# CREATE TRAFFIC QUBO
# ============================================================

def create_traffic_qubo(
    traffic_data,
    number_to_select=None
):
    """
    Creates a QUBO model for traffic intersection optimization.

    traffic_data format:

    {
        "J1": {
            "vehicles": 80,
            "queue": 30,
            "capacity": 100
        }
    }

    Supports 4 to 8 intersections.
    """

    # --------------------------------------------------------
    # GET INTERSECTIONS
    # --------------------------------------------------------

    intersections = list(
        traffic_data.keys()
    )

    n = len(intersections)


    # --------------------------------------------------------
    # CHECK NUMBER OF INTERSECTIONS
    # --------------------------------------------------------

    if n < 4 or n > 8:

        raise ValueError(
            "The traffic network must contain "
            "between 4 and 8 intersections."
        )


    # --------------------------------------------------------
    # AUTOMATIC NUMBER OF SELECTIONS
    # --------------------------------------------------------

    if number_to_select is None:

        number_to_select = max(
            2,
            n // 2
        )


    if number_to_select > n:

        raise ValueError(
            "Number of selected intersections "
            "cannot be greater than the total "
            "number of intersections."
        )


    # --------------------------------------------------------
    # CREATE QUBO MATRIX
    # --------------------------------------------------------

    Q = np.zeros(
        (n, n),
        dtype=float
    )


    # --------------------------------------------------------
    # CALCULATE TRAFFIC PRESSURE
    # --------------------------------------------------------

    pressure = []

    for intersection in intersections:

        vehicles = traffic_data[
            intersection
        ]["vehicles"]

        queue = traffic_data[
            intersection
        ]["queue"]

        capacity = traffic_data[
            intersection
        ]["capacity"]


        # ----------------------------------------------------
        # CHECK CAPACITY
        # ----------------------------------------------------

        if capacity <= 0:

            raise ValueError(
                f"Capacity of {intersection} "
                f"must be greater than zero."
            )


        # ----------------------------------------------------
        # CONGESTION RATIO
        # ----------------------------------------------------

        congestion = (
            (vehicles + queue)
            / capacity
        )


        # ----------------------------------------------------
        # TRAFFIC PRESSURE
        # ----------------------------------------------------

        traffic_pressure = (
            vehicles
            + queue
            + (congestion * 50)
        )


        pressure.append(
            traffic_pressure
        )


    # --------------------------------------------------------
    # PENALTY
    # --------------------------------------------------------

    penalty = (
        max(pressure) * 2
    )


    # ========================================================
    # DIAGONAL QUBO TERMS
    # ========================================================

    for i in range(n):

        Q[i][i] = (

            -pressure[i]

            + penalty
            * (
                1
                - 2 * number_to_select
            )
        )


    # ========================================================
    # OFF-DIAGONAL QUBO TERMS
    # ========================================================

    for i in range(n):

        for j in range(
            i + 1,
            n
        ):

            Q[i][j] = (
                2 * penalty
            )


    # --------------------------------------------------------
    # RETURN RESULTS
    # --------------------------------------------------------

    return (
        intersections,
        Q,
        pressure
    )


# ============================================================
# TEST DATA
# ============================================================

if __name__ == "__main__":

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


    # ========================================================
    # CREATE QUBO
    # ========================================================

    (
        intersections,
        Q,
        pressure
    ) = create_traffic_qubo(
        traffic_data
    )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print()
    print("==============================================")
    print(" TRAFFIC QUBO MODEL")
    print("==============================================")


    print()
    print(
        "Number of intersections:",
        len(intersections)
    )


    print()
    print("Intersections:")

    for intersection in intersections:

        print(
            f"  {intersection}"
        )


    print()
    print("Traffic pressure:")

    for i in range(
        len(intersections)
    ):

        print(
            f"  {intersections[i]} -> "
            f"{pressure[i]:.2f}"
        )


    print()
    print("QUBO Matrix:")

    print(Q)


    print()
    print("==============================================")
    print(" QUBO MODEL CREATED SUCCESSFULLY")
    print("==============================================")