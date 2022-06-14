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
random_scale = 0.6
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
        self.theta = 0.3

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

            _color = list(RED)
            factor = 1 / DEQUE_MAXLEN
            for _x, _y in zip(reversed(self.xs), reversed(self.ys)):
                _color[0] = int(RED[0] * (1 - factor) + GRAY[0] * factor)
                _color[1] = int(RED[1] * (1 - factor) + GRAY[1] * factor)
                _color[2] = int(RED[2] * (1 - factor) + GRAY[2] * factor)
                factor += 1 / DEQUE_MAXLEN
                pygame.draw.circle(self.game_display, tuple(_color), (_x, _y), 2)

            pygame.display.update()
            self.clock.tick(dt * 1000)
        self.stop_game_thread()

    def start_game_thread(self):
        self.thread = threading.Thread(target=self.game_loop, args=(), daemon=True)
        self.thread.start()

    def stop_game_thread(self):
        pygame.quit()


def main():
    x = 300
    y = 300
    theta = 0.3
    v = 1
    to_loop = True
    random_scale = 0.6
    DEQUE_MAXLEN = 100
    pygame.init()

    game_display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Going in circles")
    game_display.fill(GRAY)

    clock = pygame.time.Clock()

    xs = deque([], maxlen=DEQUE_MAXLEN)
    xs.append(x)
    ys = deque([], maxlen=DEQUE_MAXLEN)
    ys.append(y)

    while to_loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                to_loop = False
            print(event)

        game_display.fill(GRAY)
        theta = theta + (random.random() - 0.5) * random_scale
        x = x + v * math.cos(theta)
        y = y + v * math.sin(theta)

        xs.append(x)
        ys.append(y)

        _color = list(RED)
        factor = 1 / DEQUE_MAXLEN
        for _x, _y in zip(reversed(xs), reversed(ys)):
            _color[0] = int(RED[0] * (1 - factor) + GRAY[0] * factor)
            _color[1] = int(RED[1] * (1 - factor) + GRAY[1] * factor)
            _color[2] = int(RED[2] * (1 - factor) + GRAY[2] * factor)
            factor += 1 / DEQUE_MAXLEN
            pygame.draw.circle(game_display, tuple(_color), (_x, _y), 2)

        pygame.display.update()
        clock.tick(dt * 1000)

    pygame.quit()
    quit()


if __name__ == "__main__":
    go = TwoDRandomWalkSimulation()
    go.start_game_thread()
    while True:
        time.sleep(1)
    # main()
