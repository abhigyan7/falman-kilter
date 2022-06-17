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


dt = 0.1

x = 300
y = 300
theta = 0.3
v = 1
to_loop = True
random_scale = 0.7
DEQUE_MAXLEN = 100


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
        self.estimated_xs = deque([], maxlen=DEQUE_MAXLEN)
        self.predicted_xs = deque([], maxlen=DEQUE_MAXLEN)

        self.sensor_ys = deque([], maxlen=DEQUE_MAXLEN)
        self.estimated_ys = deque([], maxlen=DEQUE_MAXLEN)
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
            draw_trail(
                self.game_display, self.estimated_xs, self.estimated_ys, BLUE, 10
            )
            # draw_trail(
            #     self.game_display, self.predicted_xs, self.predicted_ys, GREEN, 10
            # )
            # _color = list(RED)
            # factor = 1 / DEQUE_MAXLEN
            # for _x, _y in zip(reversed(self.xs), reversed(self.ys)):
            #    _color[0] = int(RED[0] * (1 - factor) + GRAY[0] * factor)
            #    _color[1] = int(RED[1] * (1 - factor) + GRAY[1] * factor)
            #    _color[2] = int(RED[2] * (1 - factor) + GRAY[2] * factor)
            #    factor += 1 / DEQUE_MAXLEN
            #    pygame.draw.circle(self.game_display, tuple(_color), (_x, _y), 2)

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

    def add_estimate(self, estimate):
        self.estimated_xs.append(estimate[:, 0])
        self.estimated_ys.append(estimate[:, 1])
        return


class TwoDSecondOrderKalmanFilter(object):
    def __init__(self):
        self.xy = np.zeros((2)) + 300
        pass

    def predict(self, dt):
        return self.xy

    def estimate(self, new_data, dt):
        self.xy = self.xy * 0.1 + new_data * 0.9
        return self.xy


if __name__ == "__main__":
    kf = TwoDSecondOrderKalmanFilter()
    sim = TwoDRandomWalkSimulation((1280, 720))
    sim.start_game_thread()
    sim_is_alive = True
    while sim_is_alive:

        observation = sim.observe()
        estimate = kf.estimate(observation, 0.3)

        sim.add_estimate(estimate)
        prediction = kf.predict(1)
        sim.add_prediction(prediction)

        print(observation)
        print(estimate)
        print(prediction)
        print("*" * 20)
        time.sleep(0.3)

        sim_is_alive = sim.to_loop
    # main()
