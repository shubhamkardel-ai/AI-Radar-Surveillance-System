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

        # AI Attributes
        self.threat = "LOW"
        self.threat_score = 0
        self.intent = "UNKNOWN"
        self.camera_object = None

        # Flight trail
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

        if len(self.trail) > 60:
            self.trail.pop(0)

    def draw(self, screen):

        angle = math.radians(self.heading)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        for i, point in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail))

            trail_surface = pygame.Surface((10, 10), pygame.SRCALPHA)

            pygame.draw.circle(
                trail_surface,
                (*self.color, alpha),
                (5, 5),
                4
            )

            screen.blit(
                trail_surface,
                (point[0] - 5, point[1] - 5)
            )

        # Draw aircraft icon

        angle = math.radians(-self.heading)

        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        def rotate(px, py):
            return (
                self.x + px * cos_a - py * sin_a,
                self.y + px * sin_a + py * cos_a
            )

        if self.type == "Friendly":

            glow = pygame.Surface((40, 40), pygame.SRCALPHA)

            pygame.draw.circle(
                glow,
                (0, 255, 70, 60),
                (20, 20),
                14
            )

            screen.blit(
                glow,
                (self.x - 20, self.y - 20)
            )

            # Main body
            pygame.draw.polygon(
                screen,
                self.color,
                [
                    rotate(0, -14),  # Nose
                    rotate(-4, -4),

                    rotate(-10, 2),  # Left Wing

                    rotate(-4, 8),

                    rotate(0, 12),  # Tail

                    rotate(4, 8),

                    rotate(10, 2),  # Right Wing

                    rotate(4, -4)
                ]
            )

            # Wings
            pygame.draw.line(
                screen,
                self.color,
                rotate(-10, 0),
                rotate(10, 0),
                2
            )

            # Tail
            pygame.draw.line(
                screen,
                self.color,
                rotate(0, 6),
                rotate(0, 11),
                2
            )

            # Cockpit
            cockpit = rotate(0, -5)

            pygame.draw.circle(
                screen,
                (255, 120, 120),
                (int(cockpit[0]), int(cockpit[1])),
                2
            )
        elif self.type == "Enemy":

            angle = math.radians(-self.heading)

            sin_a = math.sin(angle)
            cos_a = math.cos(angle)

            def rotate(px, py):
                return (
                    self.x + px * cos_a - py * sin_a,
                    self.y + px * sin_a + py * cos_a
                )

            pygame.draw.polygon(
                screen,
                self.color,
                [
                    rotate(0, -14),  # Nose
                    rotate(-5, -3),

                    rotate(-12, 2),  # Left Wing

                    rotate(-5, 6),

                    rotate(-3, 12),  # Left Tail

                    rotate(3, 12),  # Right Tail

                    rotate(5, 6),

                    rotate(12, 2),  # Right Wing

                    rotate(5, -3)
                ]
            )
            glow = pygame.Surface((40, 40), pygame.SRCALPHA)

            pygame.draw.circle(
                glow,
                (255, 0, 0, 60),
                (20, 20),
                14
            )

            screen.blit(
                glow,
                (self.x - 20, self.y - 20)
            )

            if self.camera_object:
                pygame.draw.circle(
                    screen,
                    (0, 255, 255),
                    (int(self.x), int(self.y)),
                    12,
                    2
                )



        elif self.type == "Civilian":

            pygame.draw.polygon(

                screen,

                self.color,

                [

                    rotate(0, -14),  # Nose

                    rotate(-3, -6),

                    rotate(-11, -1),  # Left Wing

                    rotate(-4, 5),

                    rotate(-2, 12),  # Tail

                    rotate(2, 12),

                    rotate(4, 5),

                    rotate(11, -1),  # Right Wing

                    rotate(3, -6)

                ]

            )

            cockpit = rotate(0, -10)

            pygame.draw.circle(

                screen,

                (180, 220, 255),

                (int(cockpit[0]), int(cockpit[1])),

                2

            )

            pygame.draw.line(

                screen,

                self.color,

                rotate(-12, 0),

                rotate(12, 0),

                2

            )

            pygame.draw.line(

                screen,

                self.color,

                rotate(-6, 8),

                rotate(6, 8),

                2

            )

            cockpit = rotate(0, -8)

            pygame.draw.circle(

                screen,

                (180, 220, 255),

                (int(cockpit[0]), int(cockpit[1])),

                2

            )

        pygame.draw.circle(

            screen,

            self.color,

            rotate(0, 0),

            7,

            2

        )

        pygame.draw.circle(

            screen,

            self.color,

            rotate(0, 0),

            3

        )

        pygame.draw.line(

            screen,

            self.color,

            rotate(-8, 0),

            rotate(8, 0),

            2

        )

        pygame.draw.arc(

            screen,

            self.color,

            (

                self.x - 8,

                self.y - 8,

                16,

                16

            ),

            0,

            math.pi,

            1

        )

        arrow_length = 15

        prediction_length = 60

        end_x = self.x + math.cos(math.radians(-self.heading)) * arrow_length
        end_y = self.y - math.sin(math.radians(-self.heading)) * arrow_length

        future_x = self.x + self.vx * prediction_length
        future_y = self.y + self.vy * prediction_length

        pygame.draw.line(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            (int(end_x), int(end_y)),
            2
        )

        pygame.draw.line(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            (int(future_x), int(future_y)),
            1
        )

        pygame.draw.circle(
            screen,
            self.color,
            (int(future_x), int(future_y)),
            4,
            1
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

        if self.camera_object:
            ai_font = pygame.font.SysFont("Consolas", 11, bold=True)

            ai_text = ai_font.render(
                "AI VERIFIED",
                True,
                (0, 255, 255)
            )

            screen.blit(
                ai_text,
                (
                    int(self.x) + 8,
                    int(self.y) + 50
                )
            )

        screen.blit(
            speed_text,
            (int(self.x) + 8, int(self.y) + 5)
        )