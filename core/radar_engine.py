import math


class RadarEngine:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

        self.angle = 0
        self.speed = 0.8

    def update(self):
        self.angle += self.speed

        if self.angle >= 360:
            self.angle = 0

    def get_angle(self):
        return self.angle

    def get_end_point(self):
        radians = math.radians(self.angle)

        end_x = self.center_x + self.radius * math.cos(radians)
        end_y = self.center_y - self.radius * math.sin(radians)

        return end_x, end_y