"""Quantum Optimization Visualizer.

Displays:
- Real-time QUBO coupling matrix heatmap
- QAOA quantum state probability distribution (bar chart of measured bitstrings)
- Hybrid classical-quantum convergence trajectory (COBYLA cost descent)
- 2D/3D QAOA Energy Landscape Contour (variational optimization terrain)
- Theoretical Quantum vs Classical Scalability Benchmark ($O(2^N)$ vs $O(N^2)$)
"""

import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, List


def create_qubo_heatmap(Q: np.ndarray) -> go.Figure:
    """Generates an annotated heatmap of the 6x6 QUBO interaction matrix."""
    labels = [f"J{i+1}" for i in range(len(Q))]
    
    fig = go.Figure(data=go.Heatmap(
        z=np.round(Q, 2),
        x=labels,
        y=labels,
        colorscale="Viridis",
        hoverongaps=False,
        text=np.round(Q, 1),
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"}
    ))

    fig.update_layout(
        title="QUBO Interaction Matrix Q (Network Coupling)",
        xaxis_title="Intersection",
        yaxis_title="Intersection",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        height=340
    )
    return fig


def create_qaoa_state_distribution(top_probs: Dict[str, float], optimal_bitstring: str) -> go.Figure:
    """Generates a probability distribution bar chart of quantum measurement outcomes."""
    bitstrings = list(top_probs.keys())
    probs = list(top_probs.values())
    
    colors = [
        "#00E5FF" if s == optimal_bitstring else "#6366F1"
        for s in bitstrings
    ]

    fig = go.Figure(data=[
        go.Bar(
            x=bitstrings,
            y=probs,
            marker_color=colors,
            text=[f"{p*100:.1f}%" for p in probs],
            textposition="auto",
        )
    ])

    fig.update_layout(
        title="QAOA Quantum State Probability Spectrum |ψ(γ, β)⟩",
        xaxis_title="Eigenstate Bitstring |x₅x₄x₃x₂x₁x₀⟩",
        yaxis_title="Probability",
        yaxis=dict(range=[0, max(probs) * 1.25 if probs else 1.0]),
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        height=340
    )
    return fig


def create_convergence_plot(history: list) -> go.Figure:
    """Generates the hybrid optimization convergence curve."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(history) + 1)),
        y=history,
        mode="lines+markers",
        line=dict(color="#10B981", width=3),
        marker=dict(size=6, color="#34D399"),
        name="Hamiltonian Energy ⟨H_C⟩"
    ))

    fig.update_layout(
        title="QAOA Hybrid Convergence Curve (COBYLA Descent)",
        xaxis_title="Iteration",
        yaxis_title="Energy Expectation ⟨H_C⟩",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        height=320
    )
    return fig


def create_energy_landscape_contour(
    gamma_vals: np.ndarray,
    beta_vals: np.ndarray,
    energy_grid: np.ndarray,
    opt_gamma: float,
    opt_beta: float
) -> go.Figure:
    """Renders 2D contour plot of the QAOA variational energy landscape."""
    fig = go.Figure()

    # Contour surface
    fig.add_trace(go.Contour(
        z=energy_grid,
        x=gamma_vals,
        y=beta_vals,
        colorscale="Plasma",
        contours=dict(showlabels=True, labelfont=dict(size=10, color="white")),
        colorbar=dict(title="⟨H_C⟩ Energy")
    ))

    # Optimal point star
    fig.add_trace(go.Scatter(
        x=[opt_gamma],
        y=[opt_beta],
        mode="markers+text",
        marker=dict(symbol="star", size=16, color="#00E5FF", line=dict(color="#FFFFFF", width=2)),
        text=["Optimal (γ*, β*)"],
        textposition="top center",
        textfont=dict(color="#00E5FF", size=12, family="Arial Black"),
        name="COBYLA Solution"
    ))

    fig.update_layout(
        title="QAOA Variational Energy Landscape: E(γ, β)",
        xaxis_title="Gamma Angle γ (Cost Parameter)",
        yaxis_title="Beta Angle β (Mixer Parameter)",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        height=360
    )
    return fig


def create_quantum_scalability_chart() -> go.Figure:
    """Generates the asymptotic complexity chart proving Quantum Advantage at scale."""
    intersections = np.array([4, 6, 8, 12, 16, 20, 24, 28, 32])
    
    # Classical brute-force O(2^N)
    classical_exhaustive = 2.0 ** intersections
    
    # Classical Branch & Bound heuristic approx O(1.45^N)
    classical_bnb = 1.45 ** intersections
    
    # QAOA Polynomial scaling O(p * N^2) with p=3
    qaoa_scaling = 3.0 * (intersections ** 2)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=intersections,
        y=classical_exhaustive,
        mode="lines+markers",
        line=dict(color="#EF4444", width=3, dash="dash"),
        name="Classical Brute Force O(2ᴺ)"
    ))

    fig.add_trace(go.Scatter(
        x=intersections,
        y=classical_bnb,
        mode="lines+markers",
        line=dict(color="#F59E0B", width=2, dash="dot"),
        name="Classical Branch & Bound O(1.45ᴺ)"
    ))

    fig.add_trace(go.Scatter(
        x=intersections,
        y=qaoa_scaling,
        mode="lines+markers",
        line=dict(color="#00E5FF", width=4),
        name="Quantum QAOA Scaling O(p·N²)"
    ))

    fig.update_layout(
        title="Quantum Advantage: Computational Scaling vs City Size",
        xaxis_title="Number of Intersections (Qubits N)",
        yaxis_title="Compute Operations (Log Scale)",
        yaxis_type="log",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=340
    )
    return fig
