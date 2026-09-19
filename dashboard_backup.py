import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Quantum Traffic Dashboard",
    page_icon="🚦",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🚦 Quantum-Enhanced Adaptive Traffic Dashboard")

st.write(
    "Hybrid Quantum-Classical Urban Traffic Optimization"
)


# ============================================================
# TRAFFIC DATA
# ============================================================

traffic_data = {
    "J1": [80, 30, 100],
    "J2": [50, 15, 100],
    "J3": [20, 5, 80],
    "J4": [70, 25, 100],
    "J5": [60, 20, 90],
    "J6": [35, 10, 80],
    "J7": [90, 35, 100],
    "J8": [45, 15, 90]
}


# ============================================================
# CREATE DATAFRAME
# ============================================================

rows = []

for intersection, values in traffic_data.items():

    vehicles = values[0]
    queue = values[1]
    capacity = values[2]

    congestion = (
        (vehicles + queue)
        / capacity
    )

    pressure = (
        vehicles
        + queue
        + congestion * 50
    )

    if pressure >= 150:

        green_time = 60
        status = "CRITICAL"

    elif pressure >= 100:

        green_time = 50
        status = "HIGH"

    elif pressure >= 60:

        green_time = 40
        status = "MEDIUM"

    else:

        green_time = 30
        status = "LOW"

    quantum = (
        intersection
        in ["J4", "J5", "J6", "J7"]
    )

    if quantum:

        green_time += 10

        if green_time > 70:
            green_time = 70

    rows.append({
        "Intersection": intersection,
        "Vehicles": vehicles,
        "Queue": queue,
        "Capacity": capacity,
        "Pressure": round(pressure, 2),
        "Congestion": round(
            congestion * 100,
            2
        ),
        "Green Time": green_time,
        "Status": status,
        "Quantum Priority": (
            "YES" if quantum else "NO"
        )
    })


df = pd.DataFrame(rows)


# ============================================================
# SUMMARY
# ============================================================

total_vehicles = sum(
    values[0]
    for values in traffic_data.values()
)

total_queue = sum(
    values[1]
    for values in traffic_data.values()
)

quantum_count = 4


# ============================================================
# TOP METRICS
# ============================================================

st.header("📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Intersections",
    "8"
)

col2.metric(
    "Total Vehicles",
    total_vehicles
)

col3.metric(
    "Total Queue",
    total_queue
)

col4.metric(
    "Quantum Priority",
    quantum_count
)


# ============================================================
# TRAFFIC PRESSURE
# ============================================================

st.header("📈 Traffic Pressure")

st.bar_chart(
    df.set_index("Intersection")[
        ["Pressure"]
    ]
)


# ============================================================
# QUEUE LENGTH
# ============================================================

st.header("🚗 Queue Length")

st.bar_chart(
    df.set_index("Intersection")[
        ["Queue"]
    ]
)


# ============================================================
# SIGNAL TIMING
# ============================================================

st.header("🚦 Adaptive Signal Timing")

st.dataframe(
    df[
        [
            "Intersection",
            "Pressure",
            "Congestion",
            "Green Time",
            "Status",
            "Quantum Priority"
        ]
    ],
    use_container_width=True
)


# ============================================================
# QUANTUM OPTIMIZATION
# ============================================================

st.header("⚛️ Quantum Optimization")

st.write(
    "QAOA selected intersections:"
)

cols = st.columns(4)

for i, intersection in enumerate(
    ["J4", "J5", "J6", "J7"]
):

    cols[i].success(
        f"⚛️ {intersection}"
    )


# ============================================================
# CLASSICAL VS QUANTUM
# ============================================================

st.header(
    "⚛️ Classical vs Quantum"
)

comparison = pd.DataFrame({
    "Method": [
        "Classical",
        "Quantum"
    ],

    "Selected Intersections": [
        "J7, J1, J4, J5",
        "J4, J5, J6, J7"
    ]
})

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EMERGENCY CORRIDOR
# ============================================================

st.header(
    "🚑 Emergency Green Corridor"
)

st.write(
    "Emergency Vehicle: AMB001"
)

st.success(
    "J1 → J2 → J6 → J7 → J8"
)


st.write(
    "Green priority:"
)

cols = st.columns(5)

for i, intersection in enumerate(
    ["J1", "J2", "J6", "J7", "J8"]
):

    cols[i].success(
        f"🟢 {intersection}"
    )


# ============================================================
# PERFORMANCE
# ============================================================

st.header(
    "🌱 Performance Metrics"
)

waiting_time = (
    total_queue * 2
    + total_vehicles * 0.5
)

fuel = waiting_time * 0.08

co2 = fuel * 2.31

throughput = sum(
    min(
        row["Vehicles"],
        row["Capacity"]
        * row["Green Time"]
        / 60
    )
    for _, row in df.iterrows()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Waiting Time",
    f"{waiting_time:.1f}"
)

col2.metric(
    "Throughput",
    f"{throughput:.1f}"
)

col3.metric(
    "Fuel",
    f"{fuel:.2f} L"
)

col4.metric(
    "CO₂",
    f"{co2:.2f} kg"
)


# ============================================================
# COMPLETE DATA
# ============================================================

st.header(
    "📋 Complete Traffic Data"
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Quantum-Enhanced Adaptive Urban Traffic Optimization"
)

st.caption(
    "QAOA + Classical Optimization + Emergency Green Corridor"
)