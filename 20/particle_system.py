import math
import random
import pygame
from config import *


class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, gravity=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        if self.gravity:
            self.vy += GRAVITY * 0.5
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.rotation += self.rotation_speed

    def draw(self, surface):
        if self.life <= 0:
            return

        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)

        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)

        rotated = pygame.transform.rotate(particle_surface, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)

    @property
    def active(self):
        return self.life > 0


class FruitHalfParticle:
    def __init__(self, x, y, vx, vy, color, radius, side, fruit_type):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.side = side
        self.fruit_type = fruit_type
        self.life = 60
        self.max_life = 60
        self.rotation = 0
        self.rotation_speed = random.uniform(-8, 8)

    def update(self):
        self.vy += GRAVITY * 0.8
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.rotation += self.rotation_speed

    def draw(self, surface):
        if self.life <= 0:
            return

        alpha = int(255 * (self.life / self.max_life))

        half_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        if self.fruit_type == 'banana' or (hasattr(self, 'is_golden') and self.is_golden):
            rect = pygame.Rect(0, self.radius - 8, self.radius * 2, 16)
            if self.side == 'left':
                rect.width = self.radius
            else:
                rect.x = self.radius
                rect.width = self.radius
            pygame.draw.ellipse(half_surface, (*self.color, alpha), rect)
            pygame.draw.ellipse(half_surface, (0, 0, 0, alpha), rect, 2)
        else:
            full_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(full_surface, (*self.color, alpha), (self.radius, self.radius), self.radius)
            pygame.draw.circle(full_surface, (0, 0, 0, alpha), (self.radius, self.radius), self.radius, 2)

            mask_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            if self.side == 'left':
                pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, self.radius, self.radius * 2))
            else:
                pygame.draw.rect(mask_surface, (255, 255, 255, 255), (self.radius, 0, self.radius, self.radius * 2))

            half_surface.blit(full_surface, (0, 0))
            half_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            pygame.draw.line(half_surface, (0, 0, 0, alpha),
                           (self.radius, 0), (self.radius, self.radius * 2), 2)

        rotated = pygame.transform.rotate(half_surface, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)

    @property
    def active(self):
        return self.life > 0 and self.y < SCREEN_HEIGHT + 100


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.fruit_halves = []
        self.screen_flash = 0
        self.flash_color = (255, 0, 0)

    def create_slice_particles(self, fruit):
        angle = random.uniform(0, 360)
        for i in range(8):
            particle_angle = angle + i * 45
            speed = random.uniform(2, 5)
            vx = math.cos(math.radians(particle_angle)) * speed
            vy = math.sin(math.radians(particle_angle)) * speed - 2
            size = random.randint(3, 6)
            life = random.randint(20, 40)
            particle = Particle(fruit.x, fruit.y, vx, vy, fruit.color, size, life)
            self.particles.append(particle)

    def create_fruit_halves(self, fruit):
        split_angle = random.uniform(0, 180)
        v1x = math.cos(math.radians(split_angle)) * 4
        v1y = math.sin(math.radians(split_angle)) * 4 - 3
        v2x = math.cos(math.radians(split_angle + 180)) * 4
        v2y = math.sin(math.radians(split_angle + 180)) * 4 - 3

        half1 = FruitHalfParticle(fruit.x, fruit.y, v1x, v1y, fruit.color, fruit.radius, 'left', fruit.fruit_type)
        half2 = FruitHalfParticle(fruit.x, fruit.y, v2x, v2y, fruit.color, fruit.radius, 'right', fruit.fruit_type)

        if fruit.is_golden:
            half1.is_golden = True
            half2.is_golden = True

        self.fruit_halves.append(half1)
        self.fruit_halves.append(half2)

    def create_explosion(self, x, y):
        for i in range(20):
            angle = i * 18
            speed = random.uniform(3, 8)
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            colors = [(255, 100, 0), (255, 50, 0), (255, 200, 0), (100, 100, 100)]
            color = random.choice(colors)
            size = random.randint(5, 10)
            life = random.randint(30, 50)
            particle = Particle(x, y, vx, vy, color, size, life, gravity=False)
            self.particles.append(particle)

        for i in range(15):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 4)
            vx = math.cos(math.radians(angle)) * speed
            vy = math.sin(math.radians(angle)) * speed
            particle = Particle(x, y, vx, vy, (150, 150, 150), random.randint(3, 6), 40, gravity=True)
            self.particles.append(particle)

        self.screen_flash = 15
        self.flash_color = (255, 0, 0)

    def create_score_popup(self, x, y, score, color=(255, 255, 255)):
        pass

    def update(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.active]

        for half in self.fruit_halves:
            half.update()
        self.fruit_halves = [h for h in self.fruit_halves if h.active]

        if self.screen_flash > 0:
            self.screen_flash -= 1

    def draw(self, surface):
        for half in self.fruit_halves:
            half.draw(surface)

        for particle in self.particles:
            particle.draw(surface)

        if self.screen_flash > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(150 * (self.screen_flash / 15))
            flash_surface.fill((*self.flash_color, alpha))
            surface.blit(flash_surface, (0, 0))

    def reset(self):
        self.particles = []
        self.fruit_halves = []
        self.screen_flash = 0
