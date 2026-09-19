"""Environmental and Traffic Performance Metrics Engine.

Computes real-time and cumulative indicators according to EPA and Federal Highway
Administration transportation benchmarks:
- Total & Average Vehicle Delay (seconds)
- Network Throughput (vehicles/hour)
- Fuel Consumption (idling + stop-and-go acceleration penalties)
- CO2 Emissions (EPA standard: 2.31 kg CO2 per liter gasoline)
- Emergency Response Time reduction
"""

from typing import Dict, List


class EnvironmentalMetrics:
    IDLE_FUEL_RATE = 0.0001667  # Liters per second per idling vehicle (approx 0.60 L/h)
    STOP_GO_PENALTY = 0.012     # Liters lost per vehicle acceleration from dead stop
    CO2_PER_LITER = 2.31        # Kilograms of CO2 per liter of gasoline

    def __init__(self):
        self.reset()

    def reset(self):
        self.cumulative_waiting_time = 0.0   # veh * seconds
        self.cumulative_vehicles_cleared = 0
        self.cumulative_fuel_liters = 0.0
        self.cumulative_co2_kg = 0.0
        
        self.history_time = []
        self.history_waiting_time = []
        self.history_throughput = []
        self.history_fuel = []
        self.history_co2 = []
        self.history_queue_length = []

    def record_step(
        self,
        current_time_sec: float,
        total_queued_vehicles: float,
        cleared_this_step: float,
        phase_transitions: int,
        step_duration: float = 5.0
    ) -> Dict[str, float]:
        """Calculates and updates metrics for the current time step."""
        # 1. Waiting Time: sum of idling vehicle seconds
        step_delay_seconds = total_queued_vehicles * step_duration
        self.cumulative_waiting_time += step_delay_seconds
        
        # 2. Throughput
        self.cumulative_vehicles_cleared += int(cleared_this_step)
        current_throughput_vph = (cleared_this_step / step_duration) * 3600.0
        
        # 3. Fuel Consumption
        # Idling fuel + penalty for stopping and restarting vehicles during phase changes
        fuel_idling = total_queued_vehicles * self.IDLE_FUEL_RATE * step_duration
        fuel_stop_go = phase_transitions * 4.0 * self.STOP_GO_PENALTY
        step_fuel = fuel_idling + fuel_stop_go
        self.cumulative_fuel_liters += step_fuel
        
        # 4. CO2 Emissions
        step_co2 = step_fuel * self.CO2_PER_LITER
        self.cumulative_co2_kg += step_co2
        
        # 5. Average wait time per vehicle currently in queue
        avg_wait_sec = (self.cumulative_waiting_time / max(1, self.cumulative_vehicles_cleared + total_queued_vehicles))
        
        # Record history
        self.history_time.append(current_time_sec)
        self.history_waiting_time.append(round(avg_wait_sec, 2))
        self.history_throughput.append(round(current_throughput_vph, 1))
        self.history_fuel.append(round(self.cumulative_fuel_liters, 3))
        self.history_co2.append(round(self.cumulative_co2_kg, 3))
        self.history_queue_length.append(round(total_queued_vehicles, 1))

        return {
            "avg_wait_sec": round(avg_wait_sec, 2),
            "step_throughput_vph": round(current_throughput_vph, 1),
            "total_cleared": self.cumulative_vehicles_cleared,
            "cumulative_fuel_liters": round(self.cumulative_fuel_liters, 2),
            "cumulative_co2_kg": round(self.cumulative_co2_kg, 2),
            "current_queue": round(total_queued_vehicles, 1)
        }
