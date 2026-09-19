"""QUBO (Quadratic Unconstrained Binary Optimization) & Ising Formulation

Translates real-time urban traffic conditions into a mathematical Hamiltonian:
- Objective: Minimize network-wide vehicle delay, queue lengths, spillback risks,
  and pedestrian starvation while establishing dynamic green corridors for emergency vehicles.

Decision Variable:
  x_i ∈ {0, 1} for intersection i
    0 -> Phase 0: North-South Green (East-West Red)
    1 -> Phase 1: East-West Green (North-South Red)
"""

import numpy as np
from typing import Dict, Tuple, List, Optional
from simulation.network import RoadNetwork
from simulation.events import DynamicEventManager, EmergencyVehicle


class TrafficQUBOBuilder:
    def __init__(self, network: RoadNetwork):
        self.network = network
        self.n_nodes = len(network.intersections)

    def build_qubo(
        self,
        event_mgr: Optional[DynamicEventManager] = None,
        w_queue: float = 1.0,
        w_coord: float = 2.5,
        w_capacity: float = 1.8,
        w_pedestrian: float = 1.2,
        w_emergency: float = 50.0
    ) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Constructs the QUBO matrix Q and linear vector c such that objective is:
        
        min  x^T Q x + c^T x
        where Q is an (N x N) upper-triangular or symmetric matrix and c is (N,).
        
        Also returns breakdown dict for quantum inspector UI.
        """
        N = self.n_nodes
        Q = np.zeros((N, N), dtype=float)
        c = np.zeros(N, dtype=float)
        
        breakdown = {
            "queue_terms": {},
            "coordination_edges": [],
            "capacity_penalties": {},
            "pedestrian_terms": {},
            "emergency_overrides": {}
        }
        
        # 1. QUEUE TERM (Linear cost)
        # If EW queue > NS queue, favor x_i = 1 (negative cost).
        # Cost difference = (NS_queue - EW_queue)
        for i, node in self.network.intersections.items():
            ns_q = node.ns_queue
            ew_q = node.ew_queue
            # When x_i = 1 (EW green), cost reduction is proportional to EW queue
            # When x_i = 0 (NS green), cost reduction is proportional to NS queue
            cost_linear = (ns_q - ew_q) * w_queue
            c[i] += cost_linear
            breakdown["queue_terms"][i] = {
                "ns_queue": round(ns_q, 1),
                "ew_queue": round(ew_q, 1),
                "linear_coeff": round(cost_linear, 2)
            }

        # 2. GREEN WAVE COORDINATION (Quadratic term x_i * x_j)
        # For adjacent nodes along high-traffic corridors:
        # If corridor is EW: reward x_i = 1 and x_j = 1 -> -w_coord * x_i * x_j
        # If corridor is NS: reward x_i = 0 and x_j = 0 -> penalty for mismatch: w_coord * (x_i + x_j - 2 x_i x_j)
        for u, v, data in self.network.edges:
            corridor_type = data.get("corridor", "EW_arterial")
            
            # Check if accident or closure affects this edge
            edge_weight = w_coord
            if event_mgr and "closure" in event_mgr.active_events:
                cl_edge = event_mgr.active_events["closure"]["edge"]
                if (u, v) == cl_edge or (v, u) == cl_edge:
                    edge_weight = 0.0  # Decouple coordination if road closed
            
            i, j = min(u, v), max(u, v)
            if corridor_type == "EW_arterial":
                # Reward synchronizing both to EW Green (x_i = 1, x_j = 1)
                Q[i, j] -= edge_weight
                breakdown["coordination_edges"].append({
                    "link": f"J{i+1}-J{j+1}",
                    "corridor": "EW",
                    "coupling": -edge_weight
                })
            elif corridor_type == "NS_arterial":
                # Reward synchronizing both to NS Green (x_i = 0, x_j = 0)
                # Penalty for (1 - x_i)(x_j) + x_i(1 - x_j) = x_i + x_j - 2 x_i x_j
                c[i] += edge_weight
                c[j] += edge_weight
                Q[i, j] -= 2.0 * edge_weight
                breakdown["coordination_edges"].append({
                    "link": f"J{i+1}-J{j+1}",
                    "corridor": "NS",
                    "coupling": -2.0 * edge_weight
                })

        # 3. ROAD CAPACITY & SPILLBACK PREVENTION
        # If downstream node is near saturation, discourage green phase feeding into it
        for i, node in self.network.intersections.items():
            for d in ['N', 'S', 'E', 'W']:
                app = node.approaches[d]
                if app.density > 0.80:  # High congestion threshold
                    spillback_cost = (app.density - 0.80) * 10.0 * w_capacity
                    if d in ['N', 'S']:
                        # Discourage NS Green (favor x_i = 1)
                        c[i] -= spillback_cost
                    else:
                        # Discourage EW Green (favor x_i = 0)
                        c[i] += spillback_cost
                    breakdown["capacity_penalties"][f"J{i+1}_{d}"] = round(spillback_cost, 2)

        # 4. PEDESTRIAN MOVEMENT DEMAND
        # Prolonged pedestrian wait times trigger priority phase change
        for i, node in self.network.intersections.items():
            for d in ['N', 'S', 'E', 'W']:
                app = node.approaches[d]
                if app.pedestrian_wait_time > 25.0:  # 25 seconds wait limit
                    ped_boost = (app.pedestrian_wait_time / 10.0) * w_pedestrian
                    if d in ['N', 'S']:
                        # Pedestrians cross NS during NS phase
                        c[i] -= ped_boost
                    else:
                        c[i] += ped_boost
                    breakdown["pedestrian_terms"][f"J{i+1}_{d}"] = round(ped_boost, 2)

        # 5. EMERGENCY GREEN CORRIDOR PREEMPTION
        # Dominates objective function to enforce green wave along ambulance trajectory
        if event_mgr and event_mgr.active_emergency and event_mgr.active_emergency.is_active:
            em = event_mgr.active_emergency
            curr_node = em.current_intersection
            next_node = em.next_intersection
            
            nodes_to_preempt = [curr_node]
            if next_node is not None:
                nodes_to_preempt.append(next_node)
            
            for idx in nodes_to_preempt:
                # Determine corridor direction between curr_node and next_node
                if next_node is not None:
                    # check edge corridor type
                    edge_data = self.network.graph.get_edge_data(curr_node, next_node)
                    corridor = edge_data.get("corridor", "EW_arterial") if edge_data else "EW_arterial"
                else:
                    corridor = "EW_arterial"
                
                if corridor == "EW_arterial":
                    # Force x_idx = 1 (EW Green)
                    c[idx] -= w_emergency
                    breakdown["emergency_overrides"][f"J{idx+1}"] = "LOCKED_EW_GREEN"
                else:
                    # Force x_idx = 0 (NS Green)
                    c[idx] += w_emergency
                    breakdown["emergency_overrides"][f"J{idx+1}"] = "LOCKED_NS_GREEN"

        return Q, c, breakdown

    def to_ising(self, Q: np.ndarray, c: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Converts binary QUBO (x ∈ {0, 1}) into Ising spin Hamiltonian (z ∈ {-1, +1}):
        
        Using substitution x_i = (1 - z_i) / 2:
        H_ising = sum_i h_i z_i + sum_{i < j} J_{ij} z_i z_j + offset
        """
        N = len(c)
        # Ensure symmetric Q
        Q_sym = (Q + Q.T) / 2.0
        
        # J_ij = Q_ij / 4
        J = Q_sym / 4.0
        np.fill_diagonal(J, 0.0)
        
        # h_i = - c_i / 2 - sum_j Q_ij / 4
        h = - c / 2.0 - np.sum(Q_sym, axis=1) / 4.0
        
        offset = np.sum(c) / 2.0 + np.sum(Q_sym) / 8.0
        return h, J, offset
