"""Comparison View Component.

Renders side-by-side performance analytics between Hybrid Quantum Optimization
and Classical Traffic Baselines (Fixed-Timing or Greedy Actuated).
"""

import plotly.graph_objects as go
from typing import Dict, Any
from metrics.environmental import EnvironmentalMetrics


def create_waiting_time_chart(q_metrics: EnvironmentalMetrics, c_metrics: EnvironmentalMetrics) -> go.Figure:
    """Line chart comparing Average Waiting Time over time."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=q_metrics.history_time,
        y=q_metrics.history_waiting_time,
        mode="lines",
        line=dict(color="#00E5FF", width=3),
        name="Hybrid Quantum (QAOA)"
    ))

    fig.add_trace(go.Scatter(
        x=c_metrics.history_time,
        y=c_metrics.history_waiting_time,
        mode="lines",
        line=dict(color="#F59E0B", width=2, dash="dash"),
        name="Classical Baseline"
    ))

    fig.update_layout(
        title="Average Vehicle Delay Over Time",
        xaxis_title="Simulation Time (seconds)",
        yaxis_title="Average Wait Time (seconds / vehicle)",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320
    )
    return fig


def create_co2_comparison_chart(q_metrics: EnvironmentalMetrics, c_metrics: EnvironmentalMetrics) -> go.Figure:
    """Cumulative CO2 Emissions comparison."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=q_metrics.history_time,
        y=q_metrics.history_co2,
        mode="lines",
        line=dict(color="#10B981", width=3),
        name="Hybrid Quantum (CO₂ kg)",
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.1)"
    ))

    fig.add_trace(go.Scatter(
        x=c_metrics.history_time,
        y=c_metrics.history_co2,
        mode="lines",
        line=dict(color="#EF4444", width=2, dash="dash"),
        name="Classical Baseline (CO₂ kg)"
    ))

    fig.update_layout(
        title="Cumulative CO₂ Emissions (EPA Standard)",
        xaxis_title="Simulation Time (seconds)",
        yaxis_title="Total CO₂ (kg)",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320
    )
    return fig


def create_queue_comparison_chart(q_metrics: EnvironmentalMetrics, c_metrics: EnvironmentalMetrics) -> go.Figure:
    """Network-wide Queue Length over time."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=q_metrics.history_time,
        y=q_metrics.history_queue_length,
        mode="lines",
        line=dict(color="#8B5CF6", width=3),
        name="Quantum Queues"
    ))

    fig.add_trace(go.Scatter(
        x=c_metrics.history_time,
        y=c_metrics.history_queue_length,
        mode="lines",
        line=dict(color="#94A3B8", width=2, dash="dot"),
        name="Classical Queues"
    ))

    fig.update_layout(
        title="Network-Wide Total Vehicle Queue",
        xaxis_title="Simulation Time (seconds)",
        yaxis_title="Vehicles in Queue",
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320
    )
    return fig
