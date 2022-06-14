#!/usr/bin/env python3

import math
import random
import pygame
import numpy as np
from collections import deque

GRAY = (100, 100, 100)
RED = (225, 0, 0)
BLUE = (0, 0, 225)
GREEN = (0, 225, 0)


pygame.init()


game_display = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Going in circles")
game_display.fill(GRAY)

clock = pygame.time.Clock()

dt = 0.06

x = 300
y = 300
theta = 0.3
v = 1
to_loop = True
random_scale = 0.6

DEQUE_MAXLEN = 100
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
        _color[0] = int(_color[0] * (1 - factor) + GRAY[0] * factor)
        _color[1] = int(_color[1] * (1 - factor) + GRAY[1] * factor)
        _color[2] = int(_color[2] * (1 - factor) + GRAY[2] * factor)
        pygame.draw.circle(game_display, tuple(_color), (_x, _y), 2)

    pygame.display.update()
    clock.tick(dt * 1000)

pygame.quit()
quit()
