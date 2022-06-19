#!/usr/bin/env python3
import math
import random
import pygame
import threading
import time
import numpy as np
from collections import deque

GRAY = (100, 100, 100)
RED = (225, 0, 0)
BLUE = (0, 0, 225)
GREEN = (0, 225, 0)
RND = (255, 225, 0)


dt = 0.1

x = 300
y = 300
theta = 0.3
v = 0.2
to_loop = True
random_scale = 0.1
DEQUE_MAXLEN = 200


class TwoDRandomWalkSimulation(object):
    def __init__(self, space_size=(800, 600)):

        pygame.init()
        self.game_display = pygame.display.set_mode(space_size)
        pygame.display.set_caption("Going in circles")
        self.game_display.fill(GRAY)
        self.clock = pygame.time.Clock()
        self.to_loop = True

        self.xs = deque([300], maxlen=DEQUE_MAXLEN)
        self.ys = deque([300], maxlen=DEQUE_MAXLEN)

        self.positions = deque([], maxlen=DEQUE_MAXLEN)
        self.sensor_xs = deque([], maxlen=DEQUE_MAXLEN)
        self.updated_xs = deque([], maxlen=DEQUE_MAXLEN)
        self.predicted_xs = deque([], maxlen=DEQUE_MAXLEN)

        self.sensor_ys = deque([], maxlen=DEQUE_MAXLEN)
        self.updated_ys = deque([], maxlen=DEQUE_MAXLEN)
        self.predicted_ys = deque([], maxlen=DEQUE_MAXLEN)
        self.theta = 0.0

    def game_loop(self):
        while self.to_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.to_loop = False

            self.game_display.fill(GRAY)
            self.theta = self.theta + (random.random() - 0.5) * random_scale
            x = self.xs[-1]
            y = self.ys[-1]
            self.x = x + v * math.cos(self.theta)
            self.y = y + v * math.sin(self.theta)

            self.xs.append(self.x)
            self.ys.append(self.y)

            def draw_trail(_game_display, _xs, _ys, _color, n_points=DEQUE_MAXLEN):
                _color = list(_color)
                _color_to_draw = list(_color)
                factor = 1 / n_points

                for _x, _y, _ in zip(reversed(_xs), reversed(_ys), range(n_points)):
                    _color_to_draw[0] = int(_color[0] * (1 - factor) + GRAY[0] * factor)
                    _color_to_draw[1] = int(_color[1] * (1 - factor) + GRAY[1] * factor)
                    _color_to_draw[2] = int(_color[2] * (1 - factor) + GRAY[2] * factor)
                    factor += 1 / n_points
                    pygame.draw.circle(
                        _game_display, tuple(_color_to_draw), (_x, _y), 2
                    )

                return

            draw_trail(self.game_display, self.xs, self.ys, RED)
            draw_trail(self.game_display, self.sensor_xs, self.sensor_ys, GREEN, 10)
            draw_trail(self.game_display, self.updated_xs, self.updated_ys, BLUE, 10)
            draw_trail(self.game_display, self.predicted_xs, self.predicted_ys, RND, 10)

            pygame.display.update()
            self.clock.tick(dt * 1000)
        self.stop_game_thread()

    def start_game_thread(self):
        self.thread = threading.Thread(target=self.game_loop, args=(), daemon=True)
        self.thread.start()

    def stop_game_thread(self):
        self.to_loop = False
        pygame.quit()

    def observe(self):
        mean = np.array([self.xs[-1], self.ys[-1]]).reshape((-1, 2))
        ret = np.random.normal(mean, [20, 20]).reshape((-1, 2))
        self.sensor_xs.append(ret[0][0])
        self.sensor_ys.append(ret[0][1])
        return ret

    def add_prediction(self, prediction):
        self.predicted_xs.append(prediction[:, 0])
        self.predicted_ys.append(prediction[:, 1])
        return

    def add_update(self, update):
        self.updated_xs.append(update[:, 0])
        self.updated_ys.append(update[:, 1])
        return


class TwoDSecondOrderKalmanFilter(object):
    def __init__(self):
        self.xy = np.zeros((6)) + 0.000001
        self.covar = np.eye(6) * 100
        self.K = np.zeros((6, 2)) + 0.001

    def F(self, dt):
        return np.array(
            [
                [1, dt, dt * dt / 2, 0, 0, 0],
                [0, 0, 0, 1, dt, dt * dt / 2],
                [0, 1, dt, 0, 0, 0],
                [0, 0, 0, 0, 1, dt],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 1],
            ]
        )

    def H(self):
        return np.array([[1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0]])

    def predict(self, dt):
        self.xy = self.F(dt) @ self.xy
        return np.array([[self.xy[0], self.xy[3]]])

    def update(self, new_mean, new_covar, dt):
        print(new_mean, self.xy, "apple")
        self.xy = self.xy + self.K @ (new_mean - self.H() @ self.xy)
        self.covar = self.covar - self.K @ self.H() @ self.covar
        self.K = (
            self.covar
            @ self.H().T
            @ np.linalg.inv(self.H() @ self.covar @ self.H().T + new_covar)
        )
        return np.array([[self.xy[0], self.xy[3]]])


if __name__ == "__main__":
    kf = TwoDSecondOrderKalmanFilter()
    sim = TwoDRandomWalkSimulation((1280, 720))
    sim.start_game_thread()
    sim_is_alive = True
    dt = 0.3
    while sim_is_alive:

        prediction = kf.predict(dt)
        sim.add_prediction(prediction)

        observation = sim.observe()
        new_mean = np.zeros((2))
        new_mean[0] = observation[0][0]
        new_mean[1] = observation[0][1]
        new_covar = np.eye(2) * 100
        update = kf.update(new_mean, new_covar, dt)
        sim.add_update(update)
        # print(kf.covar)

        # print(observation)
        # print(update)
        # print(prediction)
        print("*" * 20)
        time.sleep(dt)

        sim_is_alive = sim.to_loop
    # main()
