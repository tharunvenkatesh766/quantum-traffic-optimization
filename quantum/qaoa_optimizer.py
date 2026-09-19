"""QAOA (Quantum Approximate Optimization Algorithm) Solver for Traffic Signals.

Constructs parameterized QAOA quantum circuits in Qiskit 2.x to solve the
multi-intersection traffic QUBO/Ising Hamiltonian.

Executes on Qiskit Aer Statevector simulator with classical COBYLA optimization.
Includes QAOA Energy Landscape generator and Qiskit circuit representation.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Any
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


class QAOAOptimizer:
    def __init__(self, p_layers: int = 2):
        self.p_layers = p_layers
        self.last_circuit: QuantumCircuit = None
        self.last_result: Dict[str, Any] = {}

    def build_circuit(self, h: np.ndarray, J: np.ndarray, gamma: List[float], beta: List[float]) -> QuantumCircuit:
        """Constructs the QAOA ansatz circuit for n qubits with p layers."""
        n = len(h)
        qc = QuantumCircuit(n)
        
        # 1. Initial State: Equal superposition |+>^{\otimes n}
        qc.h(range(n))
        
        # 2. Alternating Cost and Mixer layers
        for p in range(self.p_layers):
            g = gamma[p]
            b = beta[p]
            
            # --- Cost Hamiltonian Layer e^{-i \gamma H_C} ---
            # Linear terms: h_i Z_i -> Rz(2 * gamma * h_i)
            for i in range(n):
                if abs(h[i]) > 1e-6:
                    qc.rz(2.0 * g * float(h[i]), i)
            
            # Quadratic terms: J_ij Z_i Z_j -> Rzz(2 * gamma * J_ij)
            for i in range(n):
                for j in range(i + 1, n):
                    if abs(J[i, j]) > 1e-6:
                        qc.rzz(2.0 * g * float(J[i, j]), i, j)
            
            # --- Mixer Hamiltonian Layer e^{-i \beta H_M} ---
            # X mixer: sum_i X_i -> Rx(2 * beta)
            for i in range(n):
                qc.rx(2.0 * b, i)
                
        return qc

    def compute_energy_and_probs(self, qc: QuantumCircuit, h: np.ndarray, J: np.ndarray, offset: float) -> Tuple[float, Dict[str, float]]:
        """Computes the expectation value <H_C> and full probability distribution from statevector."""
        sv = Statevector.from_instruction(qc)
        probs = sv.probabilities_dict()
        n = len(h)
        
        exp_energy = 0.0
        for bitstr, p in probs.items():
            # bitstr in Qiskit order: q_{n-1}...q_0 -> reverse to index i = bit[i]
            bits = np.array([int(bitstr[n - 1 - i]) for i in range(n)], dtype=int)
            # spin: z_i = 1 - 2*x_i
            z = 1.0 - 2.0 * bits
            
            # Energy: sum h_i z_i + sum J_ij z_i z_j + offset
            e_val = np.sum(h * z) + np.sum(J * np.outer(z, z)) + offset
            exp_energy += p * e_val
            
        return float(exp_energy), probs

    def solve(self, Q: np.ndarray, c: np.ndarray, h: np.ndarray, J: np.ndarray, offset: float, max_iter: int = 25) -> Dict[str, Any]:
        """Runs the hybrid quantum-classical optimization loop using COBYLA."""
        n = len(c)
        convergence_history = []
        
        # Objective function for classical optimizer
        def objective(params):
            gamma = params[:self.p_layers]
            beta = params[self.p_layers:]
            qc = self.build_circuit(h, J, gamma, beta)
            energy, _ = self.compute_energy_and_probs(qc, h, J, offset)
            convergence_history.append(energy)
            return energy

        # Initial parameter guess
        init_params = np.concatenate([
            np.full(self.p_layers, 0.35),  # gamma
            np.full(self.p_layers, 0.55)   # beta
        ])

        # Classical optimization
        res = minimize(
            objective,
            init_params,
            method='COBYLA',
            options={'maxiter': max_iter, 'tol': 1e-3}
        )

        opt_gamma = res.x[:self.p_layers]
        opt_beta = res.x[self.p_layers:]

        # Final optimal circuit and probability sampling
        final_qc = self.build_circuit(h, J, opt_gamma, opt_beta)
        self.last_circuit = final_qc
        final_energy, all_probs = self.compute_energy_and_probs(final_qc, h, J, offset)

        # Find best bitstring (maximum probability state)
        best_bitstr = max(all_probs.items(), key=lambda item: item[1])[0]
        best_x = [int(best_bitstr[n - 1 - i]) for i in range(n)]

        # Direct QUBO objective on best bitstring
        best_x_vec = np.array(best_x)
        qubo_val = float(best_x_vec.T @ Q @ best_x_vec + c.T @ best_x_vec)

        # Top 8 state probabilities for UI charts
        sorted_states = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)[:8]
        top_probs = {k: float(v) for k, v in sorted_states}

        result = {
            "optimal_phases": {i: best_x[i] for i in range(n)},
            "optimal_bitstring": "".join(map(str, best_x)),
            "optimal_energy": final_energy,
            "qubo_cost": qubo_val,
            "convergence_history": convergence_history,
            "top_probabilities": top_probs,
            "optimal_gamma": [round(float(g), 3) for g in opt_gamma],
            "optimal_beta": [round(float(b), 3) for b in opt_beta],
            "circuit_depth": final_qc.depth(),
            "n_qubits": n,
            "num_gates": sum(final_qc.count_ops().values())
        }
        
        self.last_result = result
        return result

    def compute_energy_landscape(self, h: np.ndarray, J: np.ndarray, offset: float, n_points: int = 14) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Evaluates expectation value landscape over (gamma_0, beta_0) grid for visual terrain inspection."""
        gamma_vals = np.linspace(0.05, np.pi, n_points)
        beta_vals = np.linspace(0.05, np.pi / 2, n_points)
        energy_grid = np.zeros((n_points, n_points))

        for i, g in enumerate(gamma_vals):
            for j, b in enumerate(beta_vals):
                qc = self.build_circuit(h, J, [g], [b])
                e, _ = self.compute_energy_and_probs(qc, h, J, offset)
                energy_grid[j, i] = e  # matrix indexing: row=beta, col=gamma

        return gamma_vals, beta_vals, energy_grid

    def get_circuit_ascii(self) -> str:
        """Returns clean ASCII diagram of the active QAOA ansatz circuit."""
        if self.last_circuit is not None:
            return str(self.last_circuit.draw(output='text'))
        return "Circuit not yet synthesized."
