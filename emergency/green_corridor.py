# ============================================================
# EMERGENCY GREEN CORRIDOR
# ============================================================

import networkx as nx


# ============================================================
# CREATE TRAFFIC NETWORK
# ============================================================

def create_traffic_network():

    graph = nx.DiGraph()

    # --------------------------------------------------------
    # Add intersections
    # --------------------------------------------------------

    intersections = [
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
        "J6",
        "J7",
        "J8"
    ]

    graph.add_nodes_from(intersections)

    # --------------------------------------------------------
    # Horizontal roads
    # --------------------------------------------------------

    horizontal_roads = [

        ("J1", "J2", 2),
        ("J2", "J3", 2),
        ("J3", "J4", 2),

        ("J5", "J6", 2),
        ("J6", "J7", 2),
        ("J7", "J8", 2)
    ]

    # --------------------------------------------------------
    # Vertical roads
    # --------------------------------------------------------

    vertical_roads = [

        ("J1", "J5", 3),
        ("J2", "J6", 3),
        ("J3", "J7", 3),
        ("J4", "J8", 3)
    ]

    # --------------------------------------------------------
    # Add forward roads
    # --------------------------------------------------------

    for start, end, cost in horizontal_roads:

        graph.add_edge(
            start,
            end,
            weight=cost
        )

    for start, end, cost in vertical_roads:

        graph.add_edge(
            start,
            end,
            weight=cost
        )

    # --------------------------------------------------------
    # Add reverse roads
    # --------------------------------------------------------

    for start, end, cost in horizontal_roads:

        graph.add_edge(
            end,
            start,
            weight=cost
        )

    for start, end, cost in vertical_roads:

        graph.add_edge(
            end,
            start,
            weight=cost
        )

    return graph


# ============================================================
# FIND EMERGENCY ROUTE
# ============================================================

def find_emergency_route(
    source,
    destination
):

    graph = create_traffic_network()

    try:

        route = nx.shortest_path(
            graph,
            source=source,
            target=destination,
            weight="weight"
        )

        return route

    except nx.NetworkXNoPath:

        print(
            "No emergency route found."
        )

        return []


# ============================================================
# CALCULATE ROUTE COST
# ============================================================

def calculate_route_cost(
    route
):

    graph = create_traffic_network()

    total_cost = 0

    for i in range(
        len(route) - 1
    ):

        start = route[i]

        end = route[i + 1]

        if graph.has_edge(
            start,
            end
        ):

            total_cost += graph[
                start
            ][end]["weight"]

    return total_cost


# ============================================================
# ACTIVATE GREEN CORRIDOR
# ============================================================

def activate_green_corridor(
    route
):

    print()

    print(
        "Emergency Green Corridor:"
    )

    if not route:

        print(
            "No route available."
        )

        return

    for intersection in route:

        print(
            f"{intersection} -> "
            f"GREEN PRIORITY"
        )

    print()

    print(
        "Emergency corridor activated!"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    source = "J1"

    destination = "J8"

    route = find_emergency_route(
        source,
        destination
    )

    print()

    print("Emergency route:")

    print(
        " → ".join(route)
    )

    cost = calculate_route_cost(
        route
    )

    print()

    print(
        f"Route cost: {cost}"
    )

    activate_green_corridor(
        route
    )