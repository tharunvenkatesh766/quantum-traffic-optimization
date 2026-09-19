"""Traffic Simulation Engine.

Simulates dual parallel traffic networks (Hybrid Quantum vs Classical Baseline)
under identical traffic arrival demands and events to enable real-time comparative analysis.
"""

import copy
import numpy as np
from typing import Dict, Tuple, List, Optional
from simulation.network import RoadNetwork
from simulation.events import DynamicEventManager
from quantum.qubo_formulation import TrafficQUBOBuilder
from quantum.qaoa_optimizer import QAOAOptimizer
from quantum.classical_baselines import FixedTimingController, GreedyActuatedController
from metrics.environmental import EnvironmentalMetrics


class TrafficSimulationEngine:
    def __init__(self):
        self.step_time = 5.0  # seconds per simulation tick
        self.current_time = 0.0
        
        # Parallel networks with identical initial states
        self.quantum_network = RoadNetwork()
        self.classical_network = RoadNetwork()
        
        # Dynamic events
        self.event_manager = DynamicEventManager()
        
        # Optimizers & Controllers
        self.qubo_builder = TrafficQUBOBuilder(self.quantum_network)
        self.qaoa_solver = QAOAOptimizer(p_layers=2)
        self.fixed_controller = FixedTimingController(cycle_duration=45)
        self.greedy_controller = GreedyActuatedController()
        
        # Metrics trackers
        self.quantum_metrics = EnvironmentalMetrics()
        self.classical_metrics = EnvironmentalMetrics()
        
        # Active classical controller choice: 'fixed' or 'greedy'
        self.classical_mode = 'greedy'
        
        # Last quantum execution state
        self.last_qubo_breakdown = {}
        self.last_qaoa_result = {}
        self.last_qubo_matrix = np.zeros((6, 6))

    def reset(self):
        self.current_time = 0.0
        self.quantum_network = RoadNetwork()
        self.classical_network = copy.deepcopy(self.quantum_network)
        self.event_manager = DynamicEventManager()
        self.quantum_metrics.reset()
        self.classical_metrics.reset()

    def step(self) -> Dict[str, any]:
        """Advances both the Quantum and Classical simulations by one time step."""
        self.current_time += self.step_time
        
        # 1. GENERATE IDENTICAL INFLOW ARRIVALS FOR BOTH NETWORKS
        self._apply_inflow_arrivals()

        # 2. ADVANCE DYNAMIC EVENTS (Surges, Accidents, Road Closures)
        self.event_manager.step()

        # 3. CONTROLLER EXECUTION: QUANTUM (QUBO + QAOA)
        Q, c, breakdown = self.qubo_builder.build_qubo(self.event_manager)
        self.last_qubo_matrix = Q
        self.last_qubo_breakdown = breakdown
        
        h, J, offset = self.qubo_builder.to_ising(Q, c)
        qaoa_res = self.qaoa_solver.solve(Q, c, h, J, offset, max_iter=20)
        self.last_qaoa_result = qaoa_res
        
        # Apply optimal quantum phases
        quantum_phase_changes = 0
        for node_id, opt_phase in qaoa_res["optimal_phases"].items():
            current_phase = self.quantum_network.intersections[node_id].active_phase
            if current_phase != opt_phase:
                quantum_phase_changes += 1
            self.quantum_network.intersections[node_id].set_phase(opt_phase)

        # 4. CONTROLLER EXECUTION: CLASSICAL BASELINE
        if self.classical_mode == 'fixed':
            class_phases = self.fixed_controller.get_phases(self.classical_network, self.step_time)
        else:
            class_phases = self.greedy_controller.get_phases(self.classical_network)
            
        classical_phase_changes = 0
        for node_id, c_phase in class_phases.items():
            current_phase = self.classical_network.intersections[node_id].active_phase
            if current_phase != c_phase:
                classical_phase_changes += 1
            self.classical_network.intersections[node_id].set_phase(c_phase)

        # 5. DISCHARGE QUEUES (Outflow physics)
        q_cleared = self._discharge_network(self.quantum_network)
        c_cleared = self._discharge_network(self.classical_network)

        # 6. ADVANCE EMERGENCY VEHICLE IF ACTIVE
        if self.event_manager.active_emergency:
            finished = self.event_manager.active_emergency.advance(self.step_time)
            if finished:
                self.event_manager.event_history.append("🚑 Emergency Vehicle reached destination hospital safely!")

        # 7. RECORD ENVIRONMENTAL & MOBILITY METRICS
        q_total_queue = sum(n.total_queue for n in self.quantum_network.intersections.values())
        c_total_queue = sum(n.total_queue for n in self.classical_network.intersections.values())
        
        q_step_metrics = self.quantum_metrics.record_step(
            self.current_time, q_total_queue, q_cleared, quantum_phase_changes, self.step_time
        )
        c_step_metrics = self.classical_metrics.record_step(
            self.current_time, c_total_queue, c_cleared, classical_phase_changes, self.step_time
        )

        return {
            "time": self.current_time,
            "quantum": q_step_metrics,
            "classical": c_step_metrics,
            "qaoa": qaoa_res,
            "breakdown": breakdown
        }

    def _apply_inflow_arrivals(self):
        """Injects identical stochastic vehicle and pedestrian arrivals into both networks."""
        np.random.seed(int(self.current_time * 10) % 100000)
        
        for i in range(len(self.quantum_network.intersections)):
            q_node = self.quantum_network.intersections[i]
            c_node = self.classical_network.intersections[i]
            
            # Check if surge event active for node i
            surge_mult = 1.0
            if "surge" in self.event_manager.active_events:
                if i in self.event_manager.active_events["surge"]["nodes"]:
                    surge_mult = self.event_manager.active_events["surge"]["multiplier"]

            for d in ['N', 'S', 'E', 'W']:
                q_app = q_node.approaches[d]
                c_app = c_node.approaches[d]
                
                # Base arrival + Poisson variation
                rate = q_app.base_arrival_rate * surge_mult
                inflow = max(0, int(np.random.poisson(rate)))
                
                # Add to queue without exceeding physical road capacity
                q_app.queue_length = min(q_app.capacity, q_app.queue_length + inflow)
                c_app.queue_length = min(c_app.capacity, c_app.queue_length + inflow)
                
                # Pedestrian arrival
                if np.random.rand() < 0.35:
                    q_app.pedestrian_queue += 1
                    c_app.pedestrian_queue += 1
                    
                q_app.pedestrian_wait_time += self.step_time
                c_app.pedestrian_wait_time += self.step_time

    def _discharge_network(self, network: RoadNetwork) -> float:
        """Discharges vehicles through active green lights."""
        total_cleared = 0.0
        saturation_discharge = 14.0  # Max vehicles cleared per 5s green phase
        
        for node in network.intersections.values():
            if node.active_phase == 0:
                # North-South Green
                active_dirs = ['N', 'S']
            else:
                # East-West Green
                active_dirs = ['E', 'W']
                
            for d in active_dirs:
                app = node.approaches[d]
                # Clear vehicles
                cleared = min(app.queue_length, saturation_discharge)
                app.queue_length -= cleared
                total_cleared += cleared
                # Clear waiting pedestrians for this direction
                app.pedestrian_queue = 0
                app.pedestrian_wait_time = 0.0

        return total_cleared
