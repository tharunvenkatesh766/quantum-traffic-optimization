import numpy as np

from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.circuit.library import QAOAAnsatz
from qiskit_aer import AerSimulator

from scipy.optimize import minimize


# ============================================================
# 1. TRAFFIC DATA
# ============================================================

traffic_data = {
    "J1": {
        "vehicles": 80,
        "queue": 30
    },

    "J2": {
        "vehicles": 50,
        "queue": 15
    },

    "J3": {
        "vehicles": 20,
        "queue": 5
    },

    "J4": {
        "vehicles": 70,
        "queue": 25
    }
}


# ============================================================
# 2. CREATE TRAFFIC QUBO
# ============================================================

def create_traffic_qubo(
    traffic_data,
    number_to_select=2
):

    intersections = list(
        traffic_data.keys()
    )

    n = len(intersections)

    Q = np.zeros(
        (n, n)
    )

    pressure = []

    # Calculate traffic pressure
    for intersection in intersections:

        vehicles = traffic_data[
            intersection
        ]["vehicles"]

        queue = traffic_data[
            intersection
        ]["queue"]

        traffic_pressure = (
            vehicles + queue
        )

        pressure.append(
            traffic_pressure
        )

    # Penalty value
    penalty = max(pressure) * 2

    # Objective:
    #
    # Minimize:
    #
    # - traffic pressure
    #
    # + penalty *
    # (sum(x) - number_to_select)^2

    for i in range(n):

        Q[i, i] = (
            -pressure[i]
            + penalty *
            (1 - 2 * number_to_select)
        )

    # Quadratic penalty terms
    for i in range(n):

        for j in range(
            i + 1,
            n
        ):

            Q[i, j] = (
                2 * penalty
            )

    return (
        intersections,
        Q,
        pressure
    )


# ============================================================
# 3. CONVERT QUBO → ISING HAMILTONIAN
# ============================================================

def qubo_to_hamiltonian(Q):

    n = len(Q)

    pauli_terms = {}

    def add_term(
        label,
        coefficient
    ):

        if abs(coefficient) < 1e-10:
            return

        pauli_terms[label] = (
            pauli_terms.get(
                label,
                0
            )
            + coefficient
        )

    identity = "I" * n

    constant = 0.0

    # x_i = (1 - Z_i) / 2

    for i in range(n):

        a = Q[i, i]

        constant += (
            a / 2
        )

        label = ["I"] * n

        label[
            n - 1 - i
        ] = "Z"

        add_term(
            "".join(label),
            -a / 2
        )

    # x_i*x_j =
    # (1 - Z_i - Z_j + Z_i Z_j) / 4

    for i in range(n):

        for j in range(
            i + 1,
            n
        ):

            b = Q[i, j]

            if abs(b) < 1e-10:
                continue

            constant += (
                b / 4
            )

            # Z_i
            label_i = ["I"] * n

            label_i[
                n - 1 - i
            ] = "Z"

            add_term(
                "".join(label_i),
                -b / 4
            )

            # Z_j
            label_j = ["I"] * n

            label_j[
                n - 1 - j
            ] = "Z"

            add_term(
                "".join(label_j),
                -b / 4
            )

            # Z_i Z_j
            label_ij = ["I"] * n

            label_ij[
                n - 1 - i
            ] = "Z"

            label_ij[
                n - 1 - j
            ] = "Z"

            add_term(
                "".join(label_ij),
                b / 4
            )

    labels = [identity]

    coefficients = [
        constant
    ]

    for (
        label,
        coefficient
    ) in pauli_terms.items():

        labels.append(
            label
        )

        coefficients.append(
            coefficient
        )

    return SparsePauliOp(
        labels,
        coefficients
    )


# ============================================================
# 4. CREATE QAOA CIRCUIT
# ============================================================

def create_qaoa_circuit(
    cost_hamiltonian
):

    circuit = QAOAAnsatz(
        cost_operator=
        cost_hamiltonian,

        reps=1
    )

    return circuit


# ============================================================
# 5. QAOA COST FUNCTION
# ============================================================

def qaoa_cost_function(
    parameters,
    circuit,
    cost_hamiltonian
):

    # Insert beta and gamma
    bound_circuit = (
        circuit.assign_parameters(
            parameters
        )
    )

    # Simulate quantum state
    state = (
        Statevector.from_instruction(
            bound_circuit
        )
    )

    # Calculate expectation value
    energy = (
        state.expectation_value(
            cost_hamiltonian
        ).real
    )

    return energy


# ============================================================
# 6. RUN QAOA
# ============================================================

def run_qaoa(
    cost_hamiltonian
):

    circuit = (
        create_qaoa_circuit(
            cost_hamiltonian
        )
    )

    print(
        "\nQAOA Parameters:"
    )

    print(
        circuit.parameters
    )

    # Initial beta and gamma
    initial_parameters = np.array(
        [
            0.5,
            0.5
        ]
    )

    print(
        "\nStarting QAOA optimization..."
    )

    result = minimize(
        qaoa_cost_function,

        initial_parameters,

        args=(
            circuit,
            cost_hamiltonian
        ),

        method="COBYLA",

        options={
            "maxiter": 100
        }
    )

    print(
        "\nOptimization completed."
    )

    print(
        "Optimal parameters:"
    )

    print(
        result.x
    )

    print(
        "\nMinimum expected cost:"
    )

    print(
        result.fun
    )

    optimized_circuit = (
        circuit.assign_parameters(
            result.x
        )
    )

    return (
        optimized_circuit,
        result
    )


# ============================================================
# 7. SAMPLE FINAL QUANTUM CIRCUIT
# ============================================================

def sample_solution(
    circuit
):

    measured_circuit = (
        circuit.copy()
    )

    # Add measurements
    measured_circuit.measure_all()

    simulator = (
        AerSimulator()
    )

    # Convert QAOA instruction
    # into gates Aer can simulate
    measured_circuit = (
        measured_circuit.decompose(
            reps=5
        )
    )

    # Compile for Aer
    compiled_circuit = (
        transpile(
            measured_circuit,
            simulator
        )
    )

    # Run simulation
    result = simulator.run(
        compiled_circuit,
        shots=1024
    ).result()

    # Get measurement counts
    counts = (
        result.get_counts()
    )

    return counts


# ============================================================
# 8. CONVERT QUANTUM RESULT
#    TO TRAFFIC DECISIONS
# ============================================================

def get_traffic_decisions(
    best_state,
    intersections
):

    # Qiskit displays classical
    # bits in reverse order
    decision_bits = (
        best_state[::-1]
    )

    decisions = {}

    for i, intersection in enumerate(
        intersections
    ):

        if decision_bits[i] == "1":

            decisions[
                intersection
            ] = "SELECTED"

        else:

            decisions[
                intersection
            ] = "NOT SELECTED"

    return decisions


# ============================================================
# 9. DYNAMIC TRAFFIC SIGNAL TIMING
# ============================================================

def calculate_dynamic_signal_timing(
    traffic_data,
    intersections
):

    signal_timing = {}

    for intersection in intersections:

        vehicles = (
            traffic_data[
                intersection
            ]["vehicles"]
        )

        queue = (
            traffic_data[
                intersection
            ]["queue"]
        )

        # Traffic pressure
        pressure = (
            vehicles + queue
        )

        # Dynamic timing
        if pressure > 90:

            green_time = 60

            status = (
                "HIGH TRAFFIC"
            )

        elif pressure >= 50:

            green_time = 45

            status = (
                "MEDIUM TRAFFIC"
            )

        else:

            green_time = 30

            status = (
                "LOW TRAFFIC"
            )

        signal_timing[
            intersection
        ] = {

            "pressure":
                pressure,

            "green_time":
                green_time,

            "status":
                status
        }

    return signal_timing


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        " QUANTUM TRAFFIC OPTIMIZATION"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Create QUBO
    # --------------------------------------------------------

    (
        intersections,
        Q,
        pressure
    ) = create_traffic_qubo(
        traffic_data
    )

    # --------------------------------------------------------
    # Display intersections
    # --------------------------------------------------------

    print(
        "\nIntersections:"
    )

    print(
        intersections
    )

    # --------------------------------------------------------
    # Display traffic pressure
    # --------------------------------------------------------

    print(
        "\nTraffic pressure:"
    )

    for i in range(
        len(intersections)
    ):

        print(
            intersections[i],
            "->",
            pressure[i]
        )

    # --------------------------------------------------------
    # Display QUBO
    # --------------------------------------------------------

    print(
        "\nQUBO Matrix:"
    )

    print(Q)

    # --------------------------------------------------------
    # Convert QUBO to Hamiltonian
    # --------------------------------------------------------

    cost_hamiltonian = (
        qubo_to_hamiltonian(Q)
    )

    print(
        "\nCost Hamiltonian:"
    )

    print(
        cost_hamiltonian
    )

    # --------------------------------------------------------
    # Run QAOA
    # --------------------------------------------------------

    (
        optimized_circuit,
        result
    ) = run_qaoa(
        cost_hamiltonian
    )

    # --------------------------------------------------------
    # Sample optimized circuit
    # --------------------------------------------------------

    counts = sample_solution(
        optimized_circuit
    )

    # --------------------------------------------------------
    # Display quantum results
    # --------------------------------------------------------

    print(
        "\nQuantum measurement results:"
    )

    for (
        state,
        count
    ) in sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"{state} : {count}"
        )

    # --------------------------------------------------------
    # Find best quantum solution
    # --------------------------------------------------------

    best_state = max(
        counts,
        key=counts.get
    )

    print(
        "\n======================================"
    )

    print(
        " BEST QUANTUM SOLUTION"
    )

    print(
        "======================================"
    )

    print(
        "Bitstring:",
        best_state
    )

    # --------------------------------------------------------
    # Traffic decisions
    # --------------------------------------------------------

    decisions = (
        get_traffic_decisions(
            best_state,
            intersections
        )
    )

    print(
        "\nTraffic decisions:"
    )

    for intersection in intersections:

        print(
            intersection,
            "->",
            decisions[
                intersection
            ]
        )

    # --------------------------------------------------------
    # Dynamic signal timing
    # --------------------------------------------------------

    signal_timing = (
        calculate_dynamic_signal_timing(
            traffic_data,
            intersections
        )
    )

    print(
        "\n======================================"
    )

    print(
        " DYNAMIC TRAFFIC SIGNAL TIMING"
    )

    print(
        "======================================"
    )

    for intersection in intersections:

        data = signal_timing[
            intersection
        ]

        print(
            f"{intersection} -> "
            f"Pressure: "
            f"{data['pressure']} | "
            f"Green: "
            f"{data['green_time']} sec | "
            f"{data['status']}"
        )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        " FINAL QUANTUM TRAFFIC SUMMARY"
    )

    print(
        "======================================"
    )

    print(
        "Best quantum state:",
        best_state
    )

    print(
        "\nSelected intersections:"
    )

    for intersection in intersections:

        if (
            decisions[
                intersection
            ]
            == "SELECTED"
        ):

            print(
                f"  {intersection}"
            )

    print(
        "\nDynamic signal plan:"
    )

    for intersection in intersections:

        data = signal_timing[
            intersection
        ]

        print(
            f"  {intersection}: "
            f"{data['green_time']} sec "
            f"({data['status']})"
        )

    print(
        "\n======================================"
    )

    print(
        " PROGRAM COMPLETED SUCCESSFULLY"
    )

    print(
        "======================================"
    )

def get_quantum_solution(traffic_data):

    intersections, Q, pressure = create_traffic_qubo(
        traffic_data
    )

    print()
    print("==============================================")
    print(" QUANTUM OPTIMIZATION FROM MAIN CONTROLLER")
    print("==============================================")

    print()
    print("Running QAOA...")

    cost_hamiltonian = qubo_to_hamiltonian(Q)

    optimized_circuit, result = run_qaoa(
        cost_hamiltonian
    )

    print()
    print("Optimal QAOA parameters:")
    print(result.x)

    print()
    print("Minimum expected cost:")
    print(result.fun)

    counts = sample_solution(
        optimized_circuit
    )

    best_state = max(
        counts,
        key=counts.get
    )

    print()
    print("Best quantum state:")
    print(best_state)

    decision_bits = best_state[::-1]

    selected_intersections = []

    print()
    print("Quantum traffic decisions:")

    for i in range(
        len(intersections)
    ):

        if decision_bits[i] == "1":

            selected_intersections.append(
                intersections[i]
            )

            print(
                f"{intersections[i]} -> SELECTED"
            )

        else:

            print(
                f"{intersections[i]} -> NOT SELECTED"
            )

    return selected_intersections



def optimize_traffic_for_api(traffic_data):

    # Create QUBO using live traffic data
    intersections, Q, pressure = create_traffic_qubo(
        traffic_data,
        number_to_select=2
    )

    # Convert QUBO to Hamiltonian
    cost_hamiltonian = qubo_to_hamiltonian(Q)

    # Run QAOA
    optimized_circuit, result = run_qaoa(
        cost_hamiltonian
    )

    # Get quantum measurement results
    counts = sample_solution(
        optimized_circuit
    )

    # Find most frequent quantum state
    best_state = max(
        counts,
        key=counts.get
    )

    # Convert quantum state to decisions
    decisions = get_traffic_decisions(
        best_state,
        intersections
    )

    # Calculate dynamic timings
    signal_timing = calculate_dynamic_signal_timing(
        traffic_data,
        intersections
    )

    # Extract selected intersections
    selected_intersections = [
        intersection
        for intersection in intersections
        if decisions[intersection] == "SELECTED"
    ]

    # Create optimized signal output
    optimized_signals = {}

    for intersection in intersections:

        optimized_signals[intersection] = signal_timing[
            intersection
        ]["green_time"]

    return {
        "status": "completed",
        "method": "QAOA",
        "optimizer": "Quantum Simulation",
        "best_state": best_state,
        "selected_intersections": selected_intersections,
        "optimized_signals": optimized_signals
    }