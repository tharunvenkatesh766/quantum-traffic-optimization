"""Multi-Intersection Road Network Model for Urban Traffic Optimization.

Models 6 connected intersections in an arterial-grid configuration with:
- Directional approaches (North, South, East, West)
- Queue lengths, vehicle density, road capacity, pedestrian counts
- Signal phases and cycle management
- NetworkX topology for dynamic routing and corridor preemption
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional


class Approach:
    def __init__(self, direction: str, capacity: int = 60, base_arrival_rate: float = 6.0):
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.capacity = capacity
        self.queue_length = 8.0  # current waiting vehicles
        self.base_arrival_rate = base_arrival_rate  # vehicles per control step
        self.arrival_multiplier = 1.0  # modified during surges/events
        self.pedestrian_queue = 2
        self.pedestrian_wait_time = 0.0  # seconds waiting

    @property
    def density(self) -> float:
        return min(1.0, self.queue_length / max(1, self.capacity))


class Intersection:
    def __init__(self, node_id: int, name: str, lat: float, lon: float):
        self.id = node_id
        self.name = name
        self.lat = lat
        self.lon = lon
        
        # 4 approaches: N, S (Phase 0) and E, W (Phase 1)
        self.approaches: Dict[str, Approach] = {
            'N': Approach('N', capacity=60, base_arrival_rate=5.0),
            'S': Approach('S', capacity=60, base_arrival_rate=5.0),
            'E': Approach('E', capacity=70, base_arrival_rate=7.0),
            'W': Approach('W', capacity=70, base_arrival_rate=7.0),
        }
        
        # Phase 0: North-South Green (East-West Red)
        # Phase 1: East-West Green (North-South Red)
        self.active_phase = 0
        self.signal_color = {
            'NS': 'GREEN',
            'EW': 'RED'
        }
        self.time_in_phase = 0
        self.min_green_time = 15  # seconds
        self.max_green_time = 60  # seconds
        
        # Emergency preemption state
        self.emergency_locked = False
        self.emergency_target_phase: Optional[int] = None
        self.emergency_timeout = 0

    def set_phase(self, phase: int):
        """Sets the active signal phase and updates directional colors."""
        self.active_phase = phase
        if phase == 0:
            self.signal_color['NS'] = 'GREEN'
            self.signal_color['EW'] = 'RED'
        else:
            self.signal_color['NS'] = 'RED'
            self.signal_color['EW'] = 'GREEN'

    @property
    def total_queue(self) -> float:
        return sum(app.queue_length for app in self.approaches.values())

    @property
    def ns_queue(self) -> float:
        return self.approaches['N'].queue_length + self.approaches['S'].queue_length

    @property
    def ew_queue(self) -> float:
        return self.approaches['E'].queue_length + self.approaches['W'].queue_length

    @property
    def max_pedestrian_wait(self) -> float:
        return max(app.pedestrian_wait_time for app in self.approaches.values())


class RoadNetwork:
    """Manages the 6-intersection urban grid network and connectivity."""
    def __init__(self, center_lat: float = 37.7749, center_lon: float = -122.4194):
        # 2x3 arterial grid:
        # Node 0 (Downtown North) --- Node 1 (Central Ave)   --- Node 2 (Tech Hub East)
        #   |                           |                           |
        # Node 3 (Financial South) -- Node 4 (Market St)     --- Node 5 (Harbor Way)
        
        self.intersections: Dict[int, Intersection] = {
            0: Intersection(0, "J1: Downtown North",  center_lat + 0.005, center_lon - 0.008),
            1: Intersection(1, "J2: Central Ave",     center_lat + 0.005, center_lon),
            2: Intersection(2, "J3: Tech Hub East",   center_lat + 0.005, center_lon + 0.008),
            3: Intersection(3, "J4: Financial South", center_lat - 0.005, center_lon - 0.008),
            4: Intersection(4, "J5: Market Transit",  center_lat - 0.005, center_lon),
            5: Intersection(5, "J6: Harbor Way",      center_lat - 0.005, center_lon + 0.008),
        }
        
        # Interconnection edges (distance in meters, standard capacity)
        self.edges: List[Tuple[int, int, Dict]] = [
            (0, 1, {"distance": 550, "capacity": 100, "corridor": "EW_arterial"}),
            (1, 2, {"distance": 550, "capacity": 100, "corridor": "EW_arterial"}),
            (3, 4, {"distance": 550, "capacity": 100, "corridor": "EW_arterial"}),
            (4, 5, {"distance": 550, "capacity": 100, "corridor": "EW_arterial"}),
            (0, 3, {"distance": 600, "capacity": 90,  "corridor": "NS_arterial"}),
            (1, 4, {"distance": 600, "capacity": 110, "corridor": "NS_arterial"}),
            (2, 5, {"distance": 600, "capacity": 90,  "corridor": "NS_arterial"}),
        ]
        
        self.graph = nx.Graph()
        for node_id, node in self.intersections.items():
            self.graph.add_node(node_id, name=node.name, lat=node.lat, lon=node.lon)
        for u, v, data in self.edges:
            self.graph.add_edge(u, v, **data)

    def get_shortest_path(self, origin: int, destination: int) -> List[int]:
        """Calculates the shortest topological path for emergency preemption."""
        try:
            return nx.shortest_path(self.graph, source=origin, target=destination, weight="distance")
        except nx.NetworkXNoPath:
            return []

    def get_adjacent_intersections(self, node_id: int) -> List[int]:
        return list(self.graph.neighbors(node_id))
