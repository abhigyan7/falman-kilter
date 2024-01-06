#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

class WaterLevelSimulation:
    def __init__(
        self,
        level_sensor_noise: float = 20.0,
        max_level: float = 100.0,
        level_now: float = 30.0,
        fill_rate: float = 2.0,
        leak_rate: float = 0.1,
    ):
        self.level_sensor_var = level_sensor_noise
        self.max_level = max_level
        self.level_now = level_now
        self.fill_rate = fill_rate
        self.leak_rate = leak_rate
        return

    def step(self, dt: float, control):
        self.level_now += control * self.fill_rate * dt
        self.level_now -= self.leak_rate * dt
        return np.random.normal(self.level_now, self.level_sensor_var * dt)

    def true_value(self):
        return self.level_now

class WaterLevelController:

    def __init__(
            self,
            patience: int = 10,
            min_level_to_trigger = 80.0,
            max_level_to_trigger = 20.0,
    ):
        self.patience = patience
        self.min_level_to_trigger = min_level_to_trigger
        self.max_level_to_trigger = max_level_to_trigger
        self.patience_count = 0
        self.control_output = 0
        return

    def step(self, reading):
        if reading < self.max_level_to_trigger:
            self.patience_count += 1
        elif reading > self.min_level_to_trigger:
            self.patience_count += 1
        else:
            self.patience_count = 0

        if self.patience_count > self.patience:
            if reading < self.max_level_to_trigger:
                self.control_output = 1
            else:
                self.control_output = 0
        return self.control_output, self.patience_count


class OneDimKalmanFilter:
    def __init__(
        self,
        F: float,
        B: float,
        process_noise_var: float,
        H: float,
        init_x: float,
        init_p: float,
    ):
        self.F = F
        self.B = B
        self.process_noise_var = process_noise_var
        self.H = H

        self.x = init_x
        self.p = init_p
        return

    def predict(self, control_input: float, dt: float):
        self.x = self.F * self.x + self.B * dt * control_input
        self.p = self.p + self.process_noise_var
        return self.x, self.p

    def estimate(self, sensor_reading: float, sensor_variance: float):
        K = self.p / (self.p + sensor_variance)
        self.x = (1 - K * self.H) * self.x + K * sensor_reading
        self.p = (1 - K) * self.p
        return self.x, self.p, K

def main():

    simulation = WaterLevelSimulation()
    kalman_filter = OneDimKalmanFilter(0.99, 2.0, 2.0, 1.0, 10.0, 30.0)
    controller = WaterLevelController()

    dt = 0.5
    simulation_steps = 1000
    measurement_var = 1.0
    control_output = 0

    ts = []
    measured_levels = []
    measurement_vars = []
    filtered_levels = []
    filtered_vars = []
    predicted_levels = []
    predicted_vars = []
    control_outputs = []
    patience_counts = []
    true_levels = []
    Ks = []


    for i in range(simulation_steps):
        t = 0.0 + dt * i
        ts.append(t)

        predicted_level, predicted_var = kalman_filter.predict(control_output, dt)
        measured_level = simulation.step(dt, control_output)


        control_output, patience_count = controller.step(measured_level)

        filtered_level, filtered_var, K = kalman_filter.estimate(measured_level, sensor_variance=measurement_var)

        measured_levels.append(measured_level)
        measurement_vars.append(measurement_var)
        filtered_levels.append(filtered_level)
        filtered_vars.append(filtered_var)
        predicted_levels.append(predicted_level)
        predicted_vars.append(predicted_var)
        patience_counts.append(patience_count)
        control_outputs.append(control_output)
        true_levels.append(simulation.true_value())
        Ks.append(K)

    plt.plot(ts, measured_levels, label="measured")
    plt.plot(ts, predicted_levels, label="predicted")
    plt.plot(ts, true_levels, label="true")
    plt.plot(ts, filtered_levels, label="filtered")
    plt.ylim(0, 100)
    plt.legend(loc="best")
    plt.show()


if __name__ == "__main__":
    main()
