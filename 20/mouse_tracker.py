import math
import pygame
from config import *


class MouseTracker:
    def __init__(self):
        self.trail = []
        self.slicing = False
        self.last_mouse_pos = None

    def update(self, mouse_pos, mouse_down):
        if mouse_down:
            if not self.slicing:
                self.trail = []
                self.slicing = True
            self.trail.append(mouse_pos)
            if len(self.trail) > TRAIL_LENGTH:
                self.trail.pop(0)
        else:
            if self.slicing:
                self.slicing = False
            if len(self.trail) > 0:
                self.trail.pop(0)

    def draw(self, surface):
        if len(self.trail) < 2:
            return

        for i in range(len(self.trail) - 1):
            alpha = int(SLICE_ALPHA * (i + 1) / len(self.trail))
            color = (SLICE_COLOR[0], SLICE_COLOR[1], SLICE_COLOR[2], alpha)

            start = self.trail[i]
            end = self.trail[i + 1]

            line_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(line_surface, color, start, end, SLICE_LINE_WIDTH)
            surface.blit(line_surface, (0, 0))

    def check_collisions(self, fruits):
        sliced_fruits = []

        if len(self.trail) < 2:
            return sliced_fruits

        for i in range(len(self.trail) - 1):
            p1 = self.trail[i]
            p2 = self.trail[i + 1]

            for fruit in fruits:
                if fruit.sliced or not fruit.active:
                    continue

                if self._line_circle_intersection(p1, p2, (fruit.x, fruit.y), fruit.radius):
                    fruit.sliced = True
                    sliced_fruits.append(fruit)

        return sliced_fruits

    def _line_circle_intersection(self, p1, p2, center, radius):
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = center

        dx = x2 - x1
        dy = y2 - y1
        fx = x1 - cx
        fy = y1 - cy

        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - radius * radius

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False

        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        if 0 <= t1 <= 1:
            return True
        if 0 <= t2 <= 1:
            return True

        return False

    def reset(self):
        self.trail = []
        self.slicing = False
        self.last_mouse_pos = None
