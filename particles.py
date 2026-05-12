import random
import pygame

class Particle:
    def __init__(self, pos, color):
        self.x, self.y = pos
        self.vx = random.uniform(-5.0, 5.0)
        self.vy = random.uniform(-5.0, 5.0)
        self.color = color
        self.lifetime = 255.0
        self.decay = random.uniform(6, 14)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= self.decay

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = max(0, min(255, int(self.lifetime)))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            surface.blit(s, (self.x, self.y))


class ExpandingRing:
    def __init__(self, pos, color):
        self.x, self.y = pos
        self.radius = 5.0
        self.color = color
        self.lifetime = 255.0
        self.decay = 6.0
        self.expansion_rate = 4.0

    def update(self):
        self.radius += self.expansion_rate
        self.lifetime -= self.decay

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = max(0, min(255, int(self.lifetime)))
            s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.radius), int(self.radius)), int(self.radius), 3)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))
