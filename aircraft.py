import pygame
import math
from settings import FRIENDLY, ENEMY, CIVILIAN, UNKNOWN, HEIGHT, WIDTH

class Aircraft:

    def __init__(self, x, y, vx, vy, aircraft_type):

        self.x = x
        self.y = y

        self.vx = vx
        self.vy = vy

        self.type = aircraft_type

        self.id = ""

        self.speed = int((vx ** 2 + vy ** 2) ** 0.5)
        self.heading = 0
        self.prediction_time = 40
        self.altitude = 0
        self.distance = 0
        self.threat = "LOW"
        self.trail = []

        if self.type == "Friendly":
            self.color = FRIENDLY
        elif self.type == "Enemy":
            self.color = ENEMY
        elif self.type == "Civilian":
            self.color = CIVILIAN
        else:
            self.color = UNKNOWN

    def update(self):

        self.trail.append((self.x, self.y))

        self.x += self.vx
        self.y += self.vy

        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.heading = (angle + 360) % 360

        # Bounce from screen edges
        if self.x <= 0 or self.x >= WIDTH:
            self.vx *= -1
        if self.y <= 0 or self.y >= HEIGHT:
            self.vy *= -1

        if len(self.trail) > 20:
            self.trail.pop(0)

    def draw(self, screen):

        # Draw aircraft trail
        if self.trail:
            for i, point in enumerate(self.trail):
                alpha = int(255 * (i + 1) / len(self.trail))

                trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)

                pygame.draw.circle(
                    trail_surface,
                    (*self.color, alpha),
                    (3, 3),
                    1
                )

                screen.blit(
                    trail_surface,
                    (point[0] - 3, point[1] - 3)
                )

        # Draw aircraft
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            7
        )

        arrow_length = 15

        end_x = self.x + math.cos(math.radians(-self.heading)) * arrow_length
        end_y = self.y - math.sin(math.radians(-self.heading)) * arrow_length

        pygame.draw.line(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            (int(end_x), int(end_y)),
            2
        )

        font = pygame.font.SysFont("Consolas", 12)

        id_text = font.render(
            self.id,
            True,
            self.color
        )

        speed_text = font.render(
            f"SPD: {self.speed}",
            True,
            self.color
        )

        heading_text = font.render(
            f"HDG: {int(self.heading)}°",
            True,
            self.color
        )

        altitude_text = font.render(
            f"ALT: {self.altitude} FT",
            True,
            self.color
        )

        screen.blit(
            id_text,
            (int(self.x) + 8, int(self.y) - 10)
        )

        screen.blit(
            heading_text,
            (int(self.x) + 8, int(self.y) + 20)
        )

        screen.blit(
            altitude_text,
            (int(self.x) + 8, int(self.y) + 35)
        )

        screen.blit(
            speed_text,
            (int(self.x) + 8, int(self.y) + 5)
        )