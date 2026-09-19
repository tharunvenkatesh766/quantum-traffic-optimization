# 🚦 Quantum-Enhanced Adaptive Urban Traffic Optimization

## 📌 Project Overview

Quantum-Enhanced Adaptive Urban Traffic Optimization is a hybrid quantum-classical platform designed to optimize traffic signal timings at interconnected urban intersections.

The system analyzes traffic conditions such as vehicle density, queue length, road capacity, and signal status. It uses classical optimization and quantum optimization techniques such as **QUBO (Quadratic Unconstrained Binary Optimization)** and **QAOA (Quantum Approximate Optimization Algorithm)** to determine adaptive traffic signal decisions.

The platform also supports emergency vehicle priority through a **Green Corridor** mechanism and provides traffic performance analysis through an interactive dashboard.

---

## 🎯 Objectives

- Reduce vehicle waiting time
- Reduce traffic queue length
- Improve traffic throughput
- Optimize traffic signal timings dynamically
- Reduce fuel consumption
- Reduce CO₂ emissions
- Provide priority for emergency vehicles
- Compare classical and quantum optimization approaches
- Visualize traffic conditions through a dashboard

---

## 🚀 Key Features

### 🚗 Adaptive Traffic Signal Optimization

The system uses real-time or simulated traffic information to dynamically adjust traffic signal timings based on traffic conditions.

### ⚛️ Quantum Optimization

Traffic signal optimization is formulated as a QUBO problem and solved using QAOA-based quantum optimization.

### 🧮 Classical Optimization

Classical optimization methods are included as a baseline for comparing traffic optimization performance.

### 🚑 Emergency Green Corridor

When an emergency vehicle is detected, the system can provide a coordinated green corridor along the required route.

### 📊 Performance Analysis

The system evaluates:

- Waiting time
- Queue length
- Traffic throughput
- Fuel consumption
- CO₂ emissions

### 🖥️ Interactive Dashboard

The Java dashboard displays:

- Intersection status
- Vehicle count
- Queue length
- Traffic density
- Signal status
- Green signal timing
- Quantum optimization results
- Classical optimization results
- Emergency vehicle status
- Performance comparison

---

## 🏗️ System Architecture

```text
                Traffic Simulation / Input
                         │
                         ▼
                 Python FastAPI Backend
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
     Classical       QUBO + QAOA    Emergency
    Optimization     Optimization    Green Corridor
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 Traffic Metrics
                         │
                         ▼
                  Java Dashboard
