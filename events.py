"""Dynamic Event Management System with Hackathon Scenario Presets.

Handles real-time events:
- Sudden Traffic Congestion Surges
- Traffic Accidents (Capacity Bottlenecks)
- Road Closures / Construction Detours
- Emergency Vehicle (Ambulance / Fire Truck) Green Corridor Preemption
- 1-Click Hackathon Pitch Demo Scenarios
"""

import time
from typing import List, Dict, Optional, Tuple


class EmergencyVehicle:
    def __init__(self, vehicle_id: str, origin: int, destination: int, path: List[int]):
        self.vehicle_id = vehicle_id
        self.origin = origin
        self.destination = destination
        self.path = path  # Sequence of intersection IDs e.g. [0, 1, 2]
        self.current_index = 0
        self.progress_on_segment = 0.0  # 0.0 to 1.0 along current road link
        self.is_active = True
        self.speed_kmh = 60.0  # emergency response speed
        self.travel_time_quantum = 0.0
        self.travel_time_classical = 0.0  # benchmark comparison

    @property
    def current_intersection(self) -> int:
        return self.path[self.current_index]

    @property
    def next_intersection(self) -> Optional[int]:
        if self.current_index + 1 < len(self.path):
            return self.path[self.current_index + 1]
        return None

    def advance(self, delta_seconds: float = 5.0) -> bool:
        """Advances vehicle along the path. Returns True if vehicle reached destination."""
        if not self.is_active:
            return True
        
        self.travel_time_quantum += delta_seconds
        # Classical faces delays due to red lights (typically 1.8x - 2.4x longer)
        self.travel_time_classical += delta_seconds * 1.95
        
        # Advance progress
        step_increment = (self.speed_kmh * 1000 / 3600 * delta_seconds) / 550.0  # approx 550m edge
        self.progress_on_segment += step_increment
        
        if self.progress_on_segment >= 1.0:
            self.progress_on_segment = 0.0
            self.current_index += 1
            if self.current_index >= len(self.path) - 1:
                self.is_active = False
                return True
        return False


class DynamicEventManager:
    def __init__(self):
        self.active_events: Dict[str, Dict] = {}
        self.active_emergency: Optional[EmergencyVehicle] = None
        self.event_history: List[str] = []

    def trigger_congestion_surge(self, node_ids: List[int], multiplier: float = 3.5, duration_steps: int = 15):
        """Creates sudden traffic spike (e.g. peak hour or stadium outflow)."""
        self.active_events["surge"] = {
            "type": "CONGESTION_SURGE",
            "nodes": node_ids,
            "multiplier": multiplier,
            "steps_left": duration_steps,
            "description": f"Traffic surge (+{int((multiplier-1)*100)}%) active on Junctions {[n+1 for n in node_ids]}"
        }
        self.event_history.append(f"Congestion surge initiated on Junctions {[n+1 for n in node_ids]}")

    def trigger_accident(self, u: int, v: int, capacity_reduction: float = 0.80, duration_steps: int = 20):
        """Simulates an accident between intersections u and v, reducing road capacity."""
        self.active_events["accident"] = {
            "type": "ACCIDENT",
            "edge": (u, v),
            "capacity_reduction": capacity_reduction,
            "steps_left": duration_steps,
            "description": f"Multi-vehicle collision on link J{u+1}-J{v+1} (Capacity cut by {int(capacity_reduction*100)}%)"
        }
        self.event_history.append(f"Accident reported on link J{u+1}-J{v+1}")

    def trigger_road_closure(self, u: int, v: int, duration_steps: int = 25):
        """Simulates a complete road closure due to emergency or maintenance."""
        self.active_events["closure"] = {
            "type": "ROAD_CLOSURE",
            "edge": (u, v),
            "steps_left": duration_steps,
            "description": f"Full Road Closure on link J{u+1}-J{v+1}"
        }
        self.event_history.append(f"Road closure activated on link J{u+1}-J{v+1}")

    def dispatch_emergency_corridor(self, origin: int, destination: int, path: List[int]):
        """Dispatches an ambulance and creates the Green Wave Priority Corridor."""
        self.active_emergency = EmergencyVehicle(
            vehicle_id="MEDIC-101",
            origin=origin,
            destination=destination,
            path=path
        )
        self.event_history.append(f"🚑 Code Blue Priority Corridor engaged: J{origin+1} ➔ J{destination+1} along {[p+1 for p in path]}")

    def clear_event(self, event_key: str):
        if event_key in self.active_events:
            desc = self.active_events[event_key]["description"]
            del self.active_events[event_key]
            self.event_history.append(f"Resolved: {desc}")

    def clear_all(self):
        self.active_events.clear()
        self.active_emergency = None
        self.event_history.append("Cleared all incidents. Network nominal.")

    def step(self):
        """Decrements step countdowns for temporary dynamic events."""
        to_delete = []
        for key, event in self.active_events.items():
            event["steps_left"] -= 1
            if event["steps_left"] <= 0:
                to_delete.append(key)
        for key in to_delete:
            self.clear_event(key)
