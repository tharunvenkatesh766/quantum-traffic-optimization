from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# ============================================================
# TEAM 2 QUANTUM OPTIMIZER
# ============================================================

from quntum.quab_optimizer import optimize_traffic_for_api


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Quantum Traffic Optimization API",
    description="Backend API for Quantum-Enhanced Adaptive Urban Traffic Optimization",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TRAFFIC DATA
# ============================================================

traffic_data = {
    "intersections": [

        {
            "id": "J1",
            "name": "Intersection J1",
            "vehicles": 45,
            "queue_length": 18,
            "road_capacity": 100,
            "signal": "GREEN",
            "green_time": 35,
            "density": 45
        },

        {
            "id": "J2",
            "name": "Intersection J2",
            "vehicles": 70,
            "queue_length": 32,
            "road_capacity": 100,
            "signal": "RED",
            "green_time": 50,
            "density": 70
        },

        {
            "id": "J3",
            "name": "Intersection J3",
            "vehicles": 25,
            "queue_length": 8,
            "road_capacity": 100,
            "signal": "GREEN",
            "green_time": 25,
            "density": 25
        },

        {
            "id": "J4",
            "name": "Intersection J4",
            "vehicles": 55,
            "queue_length": 20,
            "road_capacity": 100,
            "signal": "RED",
            "green_time": 40,
            "density": 55
        },

        {
            "id": "J5",
            "name": "Intersection J5",
            "vehicles": 80,
            "queue_length": 35,
            "road_capacity": 100,
            "signal": "GREEN",
            "green_time": 45,
            "density": 80
        },

        {
            "id": "J6",
            "name": "Intersection J6",
            "vehicles": 30,
            "queue_length": 10,
            "road_capacity": 100,
            "signal": "RED",
            "green_time": 30,
            "density": 30
        }
    ]
}


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Quantum Traffic Optimization API is running",
        "status": "success",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "backend": "FastAPI",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# TRAFFIC
# ============================================================

@app.get("/traffic")
def get_traffic():

    total_vehicles = sum(
        intersection["vehicles"]
        for intersection in traffic_data["intersections"]
    )

    total_queue = sum(
        intersection["queue_length"]
        for intersection in traffic_data["intersections"]
    )

    average_density = (
        sum(
            intersection["density"]
            for intersection in traffic_data["intersections"]
        )
        / len(traffic_data["intersections"])
    )

    return {
        "timestamp": datetime.now().isoformat(),

        "total_vehicles": total_vehicles,

        "total_queue": total_queue,

        "average_density": round(
            average_density,
            2
        ),

        "intersections":
            traffic_data["intersections"]
    }


# ============================================================
# SINGLE INTERSECTION
# ============================================================

@app.get("/traffic/{intersection_id}")
def get_intersection(intersection_id: str):

    for intersection in traffic_data["intersections"]:

        if intersection["id"].upper() == intersection_id.upper():

            return {
                "status": "success",
                "intersection": intersection
            }

    return {
        "status": "error",
        "message": "Intersection not found"
    }


# ============================================================
# QUANTUM OPTIMIZATION
# TEAM 2 REAL QAOA
# ============================================================

@app.get("/optimization")
def get_optimization():

    # Convert Team 3 traffic format
    # into Team 2 optimizer format

    quantum_input = {}

    for intersection in traffic_data["intersections"]:

        intersection_id = intersection["id"]

        quantum_input[intersection_id] = {

            "vehicles":
                intersection["vehicles"],

            "queue":
                intersection["queue_length"]
        }

    # Run Team 2's actual QAOA optimizer

    result = optimize_traffic_for_api(
        quantum_input
    )

    return result


# ============================================================
# CLASSICAL OPTIMIZATION
# ============================================================

@app.get("/classical")
def get_classical():

    classical_signals = {

        "J1": 30,
        "J2": 30,
        "J3": 30,
        "J4": 30,
        "J5": 30,
        "J6": 30
    }

    return {

        "status": "completed",

        "method": "Rule-Based",

        "optimized_signals":
            classical_signals
    }


# ============================================================
# EMERGENCY GREEN CORRIDOR
# ============================================================

@app.get("/emergency")
def get_emergency():

    return {

        "active": True,

        "vehicle": "AMBULANCE",

        "route": [
            "J1",
            "J2",
            "J5",
            "J6"
        ],

        "status":
            "GREEN CORRIDOR ACTIVE",

        "estimated_time_saved":
            45
    }


# ============================================================
# SIGNAL STATUS
# ============================================================

@app.get("/signals")
def get_signals():

    signals = {}

    for intersection in traffic_data["intersections"]:

        signals[
            intersection["id"]
        ] = {

            "signal":
                intersection["signal"],

            "green_time":
                intersection["green_time"]
        }

    return {
        "signals": signals
    }


# ============================================================
# PERFORMANCE
# ============================================================

@app.get("/performance")
def get_performance():

    return {

        "classical": {

            "waiting_time": 42,

            "queue_length": 165,

            "throughput": 240,

            "fuel_consumption": 22.5,

            "co2_emission": 51.2
        },

        "quantum": {

            "waiting_time": 31,

            "queue_length": 118,

            "throughput": 286,

            "fuel_consumption": 18.5,

            "co2_emission": 42.3
        }
    }


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/dashboard")
def get_dashboard():

    total_vehicles = sum(
        intersection["vehicles"]
        for intersection in traffic_data["intersections"]
    )

    total_queue = sum(
        intersection["queue_length"]
        for intersection in traffic_data["intersections"]
    )

    average_density = (

        sum(
            intersection["density"]
            for intersection in traffic_data["intersections"]
        )

        /
        len(
            traffic_data["intersections"]
        )
    )

    return {

        "project":
            "Quantum-Enhanced Adaptive Urban Traffic Optimization",

        "network": {

            "number_of_intersections":
                len(
                    traffic_data["intersections"]
                ),

            "total_vehicles":
                total_vehicles,

            "total_queue":
                total_queue,

            "average_density":
                round(
                    average_density,
                    2
                )
        },

        "quantum": {

            "method": "QAOA",

            "status": "completed",

            "waiting_time": 31,

            "throughput": 286
        },

        "classical": {

            "method": "Rule-Based",

            "status": "completed",

            "waiting_time": 42,

            "throughput": 240
        },

        "emergency": {

            "active": True,

            "vehicle": "AMBULANCE",

            "route": [
                "J1",
                "J2",
                "J5",
                "J6"
            ]
        },

        "environment": {

            "fuel_consumption": 18.5,

            "co2_emission": 42.3
        }
    }


# ============================================================
# TEST
# ============================================================

@app.get("/test")
def test():

    return {

        "message":
            "Team 3 backend is working!",

        "traffic_api":
            "/traffic",

        "quantum_api":
            "/optimization",

        "classical_api":
            "/classical",

        "emergency_api":
            "/emergency",

        "performance_api":
            "/performance",

        "dashboard_api":
            "/dashboard"
    }