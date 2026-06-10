import random
import math
import pygame
from config import *


class Fruit:
    def __init__(self, x, fruit_type, is_golden=False, is_bomb=False):
        self.x = x
        self.y = SPAWN_Y
        self.fruit_type = fruit_type
        self.is_golden = is_golden
        self.is_bomb = is_bomb
        self.sliced = False
        self.active = True
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)

        if is_bomb:
            config = BOMB
        elif is_golden:
            config = GOLDEN_BANANA
        else:
            config = FRUIT_TYPES[fruit_type]

        self.radius = config['radius']
        self.color = config['color']
        self.score = config.get('score', 0)

        self.vx = random.uniform(MIN_VELOCITY_X, MAX_VELOCITY_X)
        self.vy = random.uniform(MIN_VELOCITY_Y, MAX_VELOCITY_Y)

    def update(self):
        if not self.active:
            return

        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed

        if self.y > SCREEN_HEIGHT + self.radius * 2:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        if self.is_bomb:
            self._draw_bomb(surface)
        else:
            self._draw_fruit(surface)

    def _draw_fruit(self, surface):
        temp_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, self.color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(temp_surface, (0, 0, 0), (self.radius, self.radius), self.radius, 2)

        if self.fruit_type == 'apple' and not self.is_golden:
            pygame.draw.rect(temp_surface, (80, 180, 80), (self.radius - 3, 5, 6, 10))
        elif self.fruit_type == 'banana' or self.is_golden:
            temp_surface2 = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surface2, self.color, (5, self.radius - 8, self.radius * 2 - 10, 16))
            pygame.draw.ellipse(temp_surface2, (0, 0, 0), (5, self.radius - 8, self.radius * 2 - 10, 16), 2)
            temp_surface = temp_surface2
        elif self.fruit_type == 'watermelon':
            for i in range(6):
                angle = i * 60
                start_x = self.radius + int(math.cos(math.radians(angle)) * self.radius * 0.3)
                start_y = self.radius + int(math.sin(math.radians(angle)) * self.radius * 0.3)
                pygame.draw.circle(temp_surface, (30, 30, 30), (start_x, start_y), 3)

        rotated = pygame.transform.rotate(temp_surface, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)

        if self.is_golden:
            glow_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            for i in range(5):
                alpha = max(0, 100 - i * 20)
                pygame.draw.circle(glow_surface, (255, 255, 150, alpha),
                                   (self.radius * 1.5, self.radius * 1.5),
                                   self.radius + i * 3, 2)
            glow_rect = glow_surface.get_rect(center=(self.x, self.y))
            surface.blit(glow_surface, glow_rect.topleft)

    def _draw_bomb(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        highlight_x = int(self.x - self.radius * 0.3)
        highlight_y = int(self.y - self.radius * 0.3)
        pygame.draw.circle(surface, (80, 80, 80), (highlight_x, highlight_y), self.radius * 0.2)

        fuse_start_x = int(self.x + self.radius * 0.3)
        fuse_start_y = int(self.y - self.radius * 0.6)
        fuse_end_x = fuse_start_x + 15
        fuse_end_y = fuse_start_y - 20
        pygame.draw.line(surface, (150, 100, 50), (fuse_start_x, fuse_start_y), (fuse_end_x, fuse_end_y), 3)

        spark_offset = math.sin(pygame.time.get_ticks() * 0.02) * 3
        pygame.draw.circle(surface, BOMB['fuse_color'],
                           (fuse_end_x + int(spark_offset), fuse_end_y - 5), 5)
        pygame.draw.circle(surface, (255, 200, 50),
                           (fuse_end_x + int(spark_offset), fuse_end_y - 5), 3)


class FruitGenerator:
    def __init__(self):
        self.fruits = []
        self.last_spawn_time = 0
        self.spawn_interval = 1500
        self.last_golden_time = 0
        self.bomb_chance = 0.15

    def update(self, current_time):
        for fruit in self.fruits:
            fruit.update()

        self.fruits = [f for f in self.fruits if f.active]

        if current_time - self.last_spawn_time > self.spawn_interval:
            self._spawn_fruit(current_time)
            self.last_spawn_time = current_time

        if current_time - self.last_golden_time > GOLDEN_BANANA['interval'] * 1000:
            self._spawn_golden_banana()
            self.last_golden_time = current_time

    def _spawn_fruit(self, current_time):
        fruit_types = list(FRUIT_TYPES.keys())
        fruit_type = random.choice(fruit_types)
        x = random.randint(100, SCREEN_WIDTH - 100)

        is_bomb = random.random() < self.bomb_chance

        fruit = Fruit(x, fruit_type, is_bomb=is_bomb)
        self.fruits.append(fruit)

        if random.random() < 0.3:
            fruit_type2 = random.choice(fruit_types)
            x2 = x + random.randint(-150, 150)
            x2 = max(100, min(SCREEN_WIDTH - 100, x2))
            fruit2 = Fruit(x2, fruit_type2)
            self.fruits.append(fruit2)

    def _spawn_golden_banana(self):
        x = random.randint(150, SCREEN_WIDTH - 150)
        fruit = Fruit(x, 'banana', is_golden=True)
        fruit.vy = random.uniform(MIN_VELOCITY_Y * 0.8, MAX_VELOCITY_Y * 0.8)
        self.fruits.append(fruit)

    def draw(self, surface):
        for fruit in self.fruits:
            if fruit.active and not fruit.sliced:
                fruit.draw(surface)

    def get_active_fruits(self):
        return [f for f in self.fruits if f.active and not f.sliced]

    def reset(self):
        self.fruits = []
        self.last_spawn_time = 0
        self.last_golden_time = 0
