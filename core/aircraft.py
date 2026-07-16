import math
import random

class Aircraft:

    def __init__(self, x, y, vx, vy, aircraft_type="Enemy"):

        self.x = x
        self.y = y

        self.vx = vx
        self.vy = vy

        self.type = aircraft_type

        self.id = f"E-{random.randint(1,999):03}"

        self.heading = 0
        self.speed = 0
        self.altitude = random.randint(2000, 12000)

        self.distance = 0

        self.threat = "LOW"
        self.threat_score = 0
        self.intent = "UNKNOWN"

        self.history = []

        self.locked = False
        self.destroyed = False

    def update(self, center=None):
        self.distance = math.sqrt(
            (self.x - center[0]) ** 2 +
            (self.y - center[1]) ** 2
        )

        self.x += self.vx
        self.y += self.vy

        self.heading = math.degrees(
            math.atan2(-self.vy, self.vx)
        )

        if self.heading < 0:
            self.heading += 360

        self.speed = int(
            math.sqrt(self.vx ** 2 + self.vy ** 2) * 100
        )

        self.history.append((self.x, self.y))

        if len(self.history) > 40:
            self.history.pop(0)

    def draw(self, screen, color=None):

        import pygame

        if color is None:

            if self.type == "Friendly":
                color = (0, 255, 70)

            elif self.type == "Enemy":
                color = (255, 60, 60)

            elif self.type == "Civilian":
                color = (70, 170, 255)

            else:
                color = (255, 220, 0)

        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            5
        )

        if self.locked:
            pygame.draw.circle(
                screen,
                (255, 255, 0),
                (int(self.x), int(self.y)),
                12,
                2
            )