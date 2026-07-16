import math


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def degrees_to_radians(angle):
    return math.radians(angle)