"""Classical Traffic Signal Baseline Controllers.

Provides standard real-world traffic management benchmarks for comparative analysis:
1. Fixed-Timing Controller (Pre-timed rigid cycle, typical legacy city signals)
2. Greedy Actuated Controller (Isolated local queue-based rule system)
3. Classical Simulated Annealing Controller (Classical heuristic QUBO benchmark)
"""

import numpy as np
from typing import Dict, List, Optional
from simulation.network import RoadNetwork


class FixedTimingController:
    """Rigid pre-timed traffic signal controller with uniform cycle lengths."""
    def __init__(self, cycle_duration: int = 45):
        self.cycle_duration = cycle_duration
        self.elapsed_time = 0

    def get_phases(self, network: RoadNetwork, step_time: float = 5.0) -> Dict[int, int]:
        self.elapsed_time += step_time
        # Cycles alternate every cycle_duration seconds
        cycle_phase = int((self.elapsed_time // self.cycle_duration) % 2)
        # All intersections cycle rigidly on fixed clock
        return {node_id: cycle_phase for node_id in network.intersections.keys()}


class GreedyActuatedController:
    """Isolated local sensor-actuated rule controller.
    
    Greedily assigns green to whichever direction has a larger local queue,
    failing to coordinate network-wide green waves or anticipate downstream spillback.
    """
    def __init__(self):
        pass

    def get_phases(self, network: RoadNetwork, emergency_override: Optional[Dict[int, int]] = None) -> Dict[int, int]:
        phases = {}
        for node_id, node in network.intersections.items():
            if emergency_override and node_id in emergency_override:
                # Rule-based priority
                phases[node_id] = emergency_override[node_id]
                continue
            
            ns_queue = node.ns_queue
            ew_queue = node.ew_queue
            
            # Isolated local greedy rule: larger queue gets green
            if ew_queue > ns_queue:
                phases[node_id] = 1
            else:
                phases[node_id] = 0
                
        return phases


class ClassicalAnnealingController:
    """Classical simulated annealing solver for QUBO comparison."""
    def __init__(self, steps: int = 300, initial_temp: float = 10.0, cooling_rate: float = 0.95):
        self.steps = steps
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate

    def get_phases(self, Q: np.ndarray, c: np.ndarray) -> Dict[int, int]:
        N = len(c)
        current_state = np.random.randint(0, 2, size=N)
        current_cost = float(current_state.T @ Q @ current_state + c.T @ current_state)
        
        best_state = current_state.copy()
        best_cost = current_cost
        temp = self.initial_temp

        for _ in range(self.steps):
            idx = np.random.randint(0, N)
            neighbor = current_state.copy()
            neighbor[idx] = 1 - neighbor[idx]
            
            neighbor_cost = float(neighbor.T @ Q @ neighbor + c.T @ neighbor)
            delta = neighbor_cost - current_cost

            if delta < 0 or np.random.rand() < np.exp(-delta / max(1e-4, temp)):
                current_state = neighbor
                current_cost = neighbor_cost
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_state = current_state.copy()

            temp *= self.cooling_rate

        return {i: int(best_state[i]) for i in range(N)}
