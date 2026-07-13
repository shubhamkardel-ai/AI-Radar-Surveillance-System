import pygame
import math
import random
import sound
import time
import cv2
from vision import Vision
from settings import *
from aircraft import Aircraft
from radar import Radar
from hub import Hub
from effects import Effects
from settings import WIDTH, HEIGHT, GREEN
from ai.intent_ai import IntentAnalyzer
from ai.fusion_ai import SensorFusion
from ai.command_ai import CommandCenter

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 18)
small_font = pygame.font.SysFont("Consolas", 14)

CENTER = (WIDTH // 2, HEIGHT // 2)

RADIUS = RADAR_RADIUS
zoom = 1.0
MIN_RADIUS = 180
MAX_RADIUS = 420

enemies = []

for _ in range(TARGET_COUNT):
    angle = random.uniform(0, 360)
    dist = random.uniform(70, RADIUS - 20)

    x = CENTER[0] + math.cos(math.radians(angle)) * dist
    y = CENTER[1] + math.sin(math.radians(angle)) * dist

    aircraft_type = random.choice(
        ["Friendly", "Enemy", "Enemy", "Civilian", "Unknown"]
    )

    aircraft = Aircraft(
        x,
        y,
        random.uniform(-2, 2),
        random.uniform(-2, 2),
        aircraft_type
    )

    aircraft.altitude = random.randint(5000, 40000)

    if aircraft_type == "Friendly":
        aircraft.id = f"F-{len([e for e in enemies if e.type == 'Friendly']) + 1:03}"
    elif aircraft_type == "Enemy":
        aircraft.id = f"E-{len([e for e in enemies if e.type == 'Enemy']) + 1:03}"
    elif aircraft_type == "Civilian":
        aircraft.id = f"C-{len([e for e in enemies if e.type == 'Civilian']) + 1:03}"
    else:
        aircraft.id = f"U-{len([e for e in enemies if e.type == 'Unknown']) + 1:03}"

    enemies.append(aircraft)

enemy_memory = [0] * len(enemies)

locked_target = None
auto_lock = True

collision_warning = False
collision_text = ""

radar = Radar()
hub = Hub(font, GREEN)
effects = Effects()
vision = Vision()
intent_ai = IntentAnalyzer()
fusion_ai = SensorFusion()
command_ai = CommandCenter()

missiles = []
smoke_particles = []
explosion_particles = []
ping_effects = []
radar_pulse = 0
missile_speed = 8
explosion_active = False
explosion_x = 0
explosion_y = 0
explosion_radius = 5

kills = 0

event_log = [
    "SYSTEM INITIALIZED"
]

mission_log = [
    "SYSTEM ONLINE",
    "RADAR INITIALIZED",
    "AI ENGINE READY"
]

missile_ready = True
reload_time = 3000      # milliseconds (3 seconds)
last_fire_time = 0

def add_log(message):

    timestamp = time.strftime("%H:%M:%S")

    mission_log.insert(
        0,
        f"{timestamp}  {message}"
    )

    if len(mission_log) > 8:
        mission_log.pop()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                current_ticks = pygame.time.get_ticks()

                if locked_target and missile_ready:
                    missiles.append({

                        "x": CENTER[0],
                        "y": CENTER[1],
                        "target": locked_target

                    })

                    event_log.append(
                        f"{time.strftime('%H:%M:%S')}  MISSILE FIRED -> {locked_target.id}"
                    )

                    add_log(f"MISSILE FIRED -> {locked_target.id}")

                    if len(event_log) > 20:
                        event_log.pop(0)

                    missile_ready = False
                    last_fire_time = current_ticks

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = pygame.mouse.get_pos()

            for aircraft in enemies:

                dx = aircraft.x - mx
                dy = aircraft.y - my

                if dx * dx + dy * dy < 25 * 25:
                    locked_target = aircraft

                    event_log.append(
                        f"{time.strftime('%H:%M:%S')}  TARGET LOCKED -> {aircraft.id}"
                    )

                    add_log(f"TARGET LOCKED -> {aircraft.id}")

                    if len(event_log) > 20:
                        event_log.pop(0)

        if event.type == pygame.MOUSEWHEEL:

            RADIUS += event.y * 10

            if RADIUS < MIN_RADIUS:
                RADIUS = MIN_RADIUS

            if RADIUS > MAX_RADIUS:
                RADIUS = MAX_RADIUS

    vision.update()

    frame = vision.frame

    fusion_ai.fuse(
        enemies,
        vision.detections
    )

    screen.fill(BLACK)

    for enemy in enemies:

        if auto_lock:

            nearest = None
            nearest_distance = 999999

            for aircraft in enemies:

                if aircraft.type != "Enemy":
                    continue

                dx = aircraft.x - CENTER[0]
                dy = aircraft.y - CENTER[1]

                d = math.sqrt(dx * dx + dy * dy)

                if d < nearest_distance:
                    nearest_distance = d
                    nearest = aircraft

            locked_target = nearest

        enemy.update()

        enemy.intent = intent_ai.analyze(enemy)

        collision_warning = False
        collision_text = ""

        for i in range(len(enemies)):

            for j in range(i + 1, len(enemies)):

                dx = enemies[i].x - enemies[j].x
                dy = enemies[i].y - enemies[j].y

                distance = math.sqrt(dx * dx + dy * dy)

                if distance < 40:
                    collision_warning = True

                    collision_text = (
                        f"{enemies[i].id} <-> {enemies[j].id}"
                    )

        enemy.threat_score = 0

        # Distance
        if enemy.distance < 120:
            enemy.threat_score += 40
        elif enemy.distance < 220:
            enemy.threat_score += 25
        else:
            enemy.threat_score += 10

        # Aircraft Type
        if enemy.type == "Enemy":
            enemy.threat_score += 40
        elif enemy.type == "Unknown":
            enemy.threat_score += 20

        # Speed
        if enemy.speed > 2:
            enemy.threat_score += 20

        # Threat Level
        if enemy.threat_score >= 80:
            enemy.threat = "HIGH"
        elif enemy.threat_score >= 50:
            enemy.threat = "MEDIUM"
        else:
            enemy.threat = "LOW"

        # ==========================
        # AI Intent Prediction
        # ==========================

        dx = CENTER[0] - enemy.x
        dy = CENTER[1] - enemy.y

        distance_to_center = math.sqrt(dx * dx + dy * dy)

        future_x = enemy.x + enemy.vx * 50
        future_y = enemy.y + enemy.vy * 50

        future_distance = math.sqrt(
            (CENTER[0] - future_x) ** 2 +
            (CENTER[1] - future_y) ** 2
        )

        if future_distance < distance_to_center:

            if enemy.type == "Enemy":
                enemy.intent = "APPROACHING"

            elif enemy.type == "Unknown":
                enemy.intent = "SUSPICIOUS"

            else:
                enemy.intent = "MOVING IN"

        else:

            if enemy.speed <= 1:
                enemy.intent = "PATROLLING"

            else:
                enemy.intent = "LEAVING AREA"

    effects.draw_scan_lines(screen)

    for r in range(80, RADIUS + 1, 80):
        pygame.draw.circle(
            screen,
            DARK_GREEN,
            CENTER,
            r,
            1
        )

        range_text = small_font.render(
            f"{r} KM",
            True,
            GREEN
        )

        screen.blit(
            range_text,
            (
                CENTER[0] + 8,
                CENTER[1] - r - 10
            )
        )

    pygame.draw.line(screen, DARK_GREEN, (CENTER[0], 0), (CENTER[0], HEIGHT))
    pygame.draw.line(
        screen,
        DARK_GREEN,
        (0, CENTER[1]),
        (WIDTH, CENTER[1])
    )

    # Degree Labels
    for degree in range(0, 360, 30):
        x = CENTER[0] + math.cos(math.radians(degree)) * (RADIUS + 20)
        y = CENTER[1] + math.sin(math.radians(degree)) * (RADIUS + 20)

        text = small_font.render(str(degree), True, GREEN)

        screen.blit(
            text,
            (
                x - text.get_width() // 2,
                y - text.get_height() // 2
            )
        )

    north = font.render(
        "N",
        True,
        LIGHT_GREEN
    )

    screen.blit(
        north,
        (
            CENTER[0] - 8,
            CENTER[1] - RADIUS - 45
        )
    )

    # Compass Directions
    compass_font = pygame.font.SysFont("Consolas", 20, bold=True)

    directions = [
        ("E", 0),
        ("S", 90),
        ("W", 180),
        ("N", 270)
    ]

    for label, angle in directions:
        x = CENTER[0] + math.cos(math.radians(angle)) * (RADIUS + 40)
        y = CENTER[1] + math.sin(math.radians(angle)) * (RADIUS + 40)

        txt = compass_font.render(label, True, LIGHT_GREEN)

        screen.blit(
            txt,
            (
                x - txt.get_width() // 2,
                y - txt.get_height() // 2
            )
        )

    for i in range(140):

        a = radar.angle + i * 2

        alpha = max(0, 220 - i)

        sweep = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        p1 = CENTER

        p2 = (
            CENTER[0] + math.cos(math.radians(a - 1)) * RADIUS,
            CENTER[1] + math.sin(math.radians(a - 1)) * RADIUS
        )

        p3 = (
            CENTER[0] + math.cos(math.radians(a + 1)) * RADIUS,
            CENTER[1] + math.sin(math.radians(a + 1)) * RADIUS
        )

        pygame.draw.polygon(
            sweep,
            (0, 255, 70, alpha),
            [p1, p2, p3],
        )

        pygame.draw.line(
            sweep,
            (150, 255, 180, alpha),
            CENTER,
            p2,
            2
        )

        screen.blit(sweep, (0, 0))

    pygame.draw.circle(
        screen,
        GREEN,
        CENTER,
        RADIUS,
        2
    )

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.circle(
        glow,
        (0, 255, 70, 18),
        CENTER,
        RADIUS,
        8
    )

    screen.blit(glow, (0, 0))

    pygame.draw.circle(
        screen,
        DARK_GREEN,
        CENTER,
        RADIUS - 25,
        1
    )

    pygame.draw.circle(
        screen,
        DARK_GREEN,
        CENTER,
        RADIUS - 50,
        1
    )

    pygame.draw.line(
        screen,
        LIGHT_GREEN,
        (CENTER[0] - 10, CENTER[1]),
        (CENTER[0] + 10, CENTER[1]),
        1
    )

    pygame.draw.line(
        screen,
        LIGHT_GREEN,
        (CENTER[0], CENTER[1] - 10),
        (CENTER[0], CENTER[1] + 10),
        1
    )

    pulse_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.circle(
        pulse_surface,
        (0, 255, 70, 40),
        CENTER,
        int(radar_pulse),
        2
    )

    screen.blit(pulse_surface, (0, 0))

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.circle(
        glow,
        (0, 255, 70, 35),
        CENTER,
        RADIUS,
        8
    )

    screen.blit(glow, (0, 0))

    pulse = 5 + int(2 * math.sin(pygame.time.get_ticks() * 0.008))

    pygame.draw.circle(
        screen,
        LIGHT_GREEN,
        CENTER,
        pulse
    )

    pygame.draw.circle(
        screen,
        GREEN,
        CENTER,
        12,
        2
    )

    pygame.draw.circle(
        screen,
        DARK_GREEN,
        CENTER,
        20,
        1
    )

    pygame.draw.line(
        screen,
        GREEN,
        CENTER,
        (
            CENTER[0] + math.cos(math.radians(radar.angle)) * 20,
            CENTER[1] + math.sin(math.radians(radar.angle)) * 20
        ),
        2
    )

    for i, enemy in enumerate(enemies):

        distance = math.sqrt(
            (enemy.x - CENTER[0]) ** 2 +
            (enemy.y - CENTER[1]) ** 2
        )

        x = enemy.x
        y = enemy.y

        enemy_angle = math.degrees(
            math.atan2(CENTER[1] - y, x - CENTER[0])
        )

        dif = abs((radar.angle - enemy_angle + 100) % 360 - 100)

        if dif < 2:

            event_log.append(
                f"{time.strftime('%H:%M:%S')}  RADAR CONTACT -> {enemy.id}"
            )

            if len(event_log) > 20:
                event_log.pop(0)

                ping_effects.append({
                    "x": enemy.x,
                    "y": enemy.y,
                    "radius": 5,
                    "alpha": 255
                })

            enemy_memory[i] = 10

        if enemy_memory[i] > 0:

            if locked_target == enemy:
                pygame.draw.rect(
                    screen,
                    RED,
                    (
                        int(enemy.x) - 18,
                        int(enemy.y) - 18,
                        36,
                        36
                    ),
                    2
                )

                pygame.draw.circle(
                    screen,
                    RED,
                    (int(enemy.x), int(enemy.y)),
                    22,
                    1
                )

                pygame.draw.circle(
                    screen,
                    (255, 60, 60),
                    (int(enemy.x), int(enemy.y)),
                    28,
                    1
                )

                lock_radius = 30 + int(2 * math.sin(pygame.time.get_ticks() * 0.01))

                pygame.draw.circle(
                    screen,
                    RED,
                    (int(enemy.x), int(enemy.y)),
                    lock_radius,
                    1
                )

                pygame.draw.line(
                    screen,
                    RED,
                    (enemy.x - 25, enemy.y),
                    (enemy.x - 18, enemy.y),
                    2
                )

                pygame.draw.line(
                    screen,
                    RED,
                    (enemy.x + 18, enemy.y),
                    (enemy.x + 25, enemy.y),
                    2
                )

                pygame.draw.line(
                    screen,
                    RED,
                    (enemy.x, enemy.y - 25),
                    (enemy.x, enemy.y - 18),
                    2
                )

                pygame.draw.line(
                    screen,
                    RED,
                    (enemy.x, enemy.y + 18),
                    (enemy.x, enemy.y + 25),
                    2
                )

                if (pygame.time.get_ticks() // 300) % 2 == 0:
                    lock_text = small_font.render(
                        "LOCKED",
                        True,
                        RED
                    )

                    screen.blit(
                        lock_text,
                        (
                            enemy.x - 28,
                            enemy.y - 45
                        )
                    )

            enemy_memory[i] -= 1

            glow = pygame.Surface((40, 40), pygame.SRCALPHA)

            pygame.draw.circle(
                glow,
                (0, 255, 70, 70),
                (20, 20),
                14
            )

            if distance <= RADIUS:
                screen.blit(glow, (x - 20, y - 20))

            if distance <= RADIUS:
                enemy.draw(screen)

    for missile in missiles[:]:

        target = missile["target"]

        if target not in enemies:
            missiles.remove(missile)
            continue

        dx = target.x - missile["x"]
        dy = target.y - missile["y"]

        distance = math.sqrt(dx * dx + dy * dy)

        if distance > missile_speed:

            missile["x"] += dx / distance * missile_speed
            missile["y"] += dy / distance * missile_speed

            smoke_particles.append([
                missile["x"],
                missile["y"],
                random.randint(8, 12)
            ])

        else:

            explosion_active = True

            explosion_x = target.x
            explosion_y = target.y

            for _ in range(30):
                explosion_particles.append({

                    "x": target.x,
                    "y": target.y,

                    "vx": random.uniform(-4, 4),
                    "vy": random.uniform(-4, 4),

                    "life": 30

                })

            if target in enemies:
                enemies.remove(target)
                kills += 1

                event_log.append(
                    f"{time.strftime('%H:%M:%S')}  TARGET DESTROYED -> {target.id}"
                )

                add_log(f"TARGET DESTROYED -> {target.id}")

                if len(event_log) > 20:
                    event_log.pop(0)

            missiles.remove(missile)

        pygame.draw.line(
            screen,
            (255, 120, 0),
            CENTER,
            (int(missile["x"]), int(missile["y"])),
            1
        )

        pygame.draw.circle(
            screen,
            RED,
            (int(missile["x"]), int(missile["y"])),
            4
        )
    current_ticks = pygame.time.get_ticks()

    if not missile_ready:

        if current_ticks - last_fire_time >= reload_time:


            missile_ready = True

    for smoke in smoke_particles[:]:

        color = random.choice([
            (255, 220, 120),
            (255, 180, 60),
            (255, 120, 20)
        ])

        pygame.draw.circle(
            screen,
            color,
            (int(smoke[0]), int(smoke[1])),
            int(smoke[2])
        )

        smoke[2] -= 0.4

        if smoke[2] <= 0:
            smoke_particles.remove(smoke)

    for ping in ping_effects[:]:

        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        pygame.draw.circle(
            surface,
            (0, 255, 70, ping["alpha"]),
            (int(ping["x"]), int(ping["y"])),
            int(ping["radius"]),
            2
        )

        screen.blit(surface, (0, 0))

        ping["radius"] += 2
        ping["alpha"] -= 15

        if ping["alpha"] <= 0:
            ping_effects.remove(ping)

    radar.update()

    radar_pulse += 3

    if radar_pulse > RADIUS:
        radar_pulse = 0
    
    # Play sound once every full rotation
    if radar.angle == 0:
        sound.play_sweep()
        radar_pulse = 0

    fps = int(clock.get_fps())
    current_time = time.strftime("%H:%M:%S")

    bearing = int(radar.angle) % 360

    bearing_text = font.render(
        f"BEARING : {bearing:03}°",
        True,
        LIGHT_GREEN
    )

    # ===================================
    # AI Command Banner
    # ===================================

    if locked_target:

        if locked_target.type == "Enemy":
            command_status = "STATUS : TRACKING ENEMY"
            command_color = RED

        elif locked_target.type == "Unknown":
            command_status = "STATUS : INVESTIGATING"
            command_color = (255, 255, 0)

        elif locked_target.type == "Friendly":
            command_status = "STATUS : FRIENDLY AIRCRAFT"
            command_color = GREEN

        else:
            command_status = "STATUS : CIVILIAN FLIGHT"
            command_color = LIGHT_GREEN

    else:

        command_status = "STATUS : SEARCHING"
        command_color = GREEN

    friendly_count = sum(1 for e in enemies if e.type == "Friendly")
    enemy_count = sum(1 for e in enemies if e.type == "Enemy")
    civilian_count = sum(1 for e in enemies if e.type == "Civilian")
    unknown_count = sum(1 for e in enemies if e.type == "Unknown")

    high_threat = sum(1 for e in enemies if e.threat == "HIGH")

    hub.draw(
        screen,
        fps,
        len(enemies),
        radar.angle
    )

    screen.blit(
        bearing_text,
        (20, HEIGHT - 35)
    )

    # ===================================
    # Draw AI Command Banner
    # ===================================

    banner_font = pygame.font.SysFont(
        "Consolas",
        22,
        bold=True
    )

    pygame.draw.line(
        screen,
        DARK_GREEN,
        (20, 20),
        (730, 20),
        2
    )

    banner = banner_font.render(
        f"AEGISAI DEFENSE GRID    {command_status}",
        True,
        command_color
    )

    screen.blit(
        banner,
        (30, 28)
    )

    pygame.draw.line(
        screen,
        DARK_GREEN,
        (20, 60),
        (730, 60),
        2
    )

    stats = [

        "RADAR STATUS",

        f"Friendly : {friendly_count}",
        f"Enemy    : {enemy_count}",
        f"Civilian : {civilian_count}",
        f"Unknown  : {unknown_count}",

        "",
        f"Locked : {locked_target.id if locked_target else 'NONE'}",

        "",
        f"High Threat : {high_threat}",

        "",
        f"KILLS : {kills}",

        "",
        f"MISSILE : {'READY' if missile_ready else 'RELOADING'}",

        "",
        f"ZOOM : {RADIUS}px",

        "",
        f"FPS : {fps}",

        "Radar : ONLINE",

        "",
        f"TIME : {current_time}"
    ]

    # ==========================
    # AI EVENT LOG
    # ==========================

    event_title = small_font.render(
        "AI EVENT LOG",
        True,
        LIGHT_GREEN
    )

    screen.blit(
        event_title,
        (20, HEIGHT - 200)
    )

    for i, event in enumerate(event_log[-6:]):
        txt = small_font.render(
            "• " + event,
            True,
            GREEN
        )

        screen.blit(
            txt,
            (20, HEIGHT - 175 + i * 20)
        )

    for i, line in enumerate(stats):
        text = small_font.render(
            line,
            True,
            GREEN
        )

        screen.blit(
            text,
            (760, 430 + i * 22)
        )

    # ===================================
    # MISSION LOG
    # ===================================

    log_x = 20
    log_y = HEIGHT - 220

    pygame.draw.rect(
        screen,
        (12, 20, 12),
        (log_x, log_y, 320, 190)
    )

    pygame.draw.rect(
        screen,
        DARK_GREEN,
        (log_x, log_y, 320, 190),
        2
    )

    log_title = font.render(
        "MISSION LOG",
        True,
        LIGHT_GREEN
    )

    screen.blit(
        log_title,
        (log_x + 10, log_y + 10)
    )

    pygame.draw.line(
        screen,
        DARK_GREEN,
        (log_x + 10, log_y + 38),
        (log_x + 310, log_y + 38),
        2
    )

    for i, message in enumerate(mission_log):
        txt = small_font.render(
            message,
            True,
            GREEN
        )

        screen.blit(
            txt,
            (
                log_x + 10,
                log_y + 50 + i * 18
            )
        )

    panel_x = WIDTH - 285
    panel_y = 95

    panel_width = 280
    panel_height = 560

    # Target Information Panel
    if locked_target:

        info_font = pygame.font.SysFont("Consolas", 16)

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (
                panel_x,
                panel_y,
                panel_width,
                panel_height
            ),
            2
        )

        pygame.draw.rect(
            screen,
            (15, 15, 15),
            (
                panel_x + 1,
                panel_y + 1,
                panel_width - 2,
                panel_height - 2
            )
        )

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (
                panel_x,
                panel_y,
                panel_width,
                38
            )
        )

        title = info_font.render(
            "AEGIS AI COMMAND CENTER",
            True,
            LIGHT_GREEN
        )

        screen.blit(
            title,
            (
                panel_x + 12,
                panel_y + 10
            )
        )

        pygame.draw.line(
            screen,
            GREEN,
            (panel_x, panel_y + 38),
            (panel_x + panel_width, panel_y + 38),
            2
        )

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (panel_x, panel_y, 240, 180),
            2
        )

        info_font = pygame.font.SysFont("Consolas", 16)

        # ==========================================
        # AEGISAI COMMAND CENTER TITLE
        # ==========================================

        title_font = pygame.font.SysFont(
            "Consolas",
            18,
            bold=True
        )

        title = title_font.render(
            "AEGISAI COMMAND CENTER",
            True,
            LIGHT_GREEN
        )

        screen.blit(
            title,
            (
                panel_x + 10,
                panel_y + 10
            )
        )

        pygame.draw.line(
            screen,
            GREEN,
            (panel_x + 10, panel_y + 38),
            (panel_x + 235, panel_y + 38),
            2
        )

        recommendations = command_ai.recommend(locked_target)

        screen.blit(
            info_font.render("TARGET DATA", True, LIGHT_GREEN),
            (panel_x + 10, panel_y + 52)
        )

        info = [

            ("TARGET ID", locked_target.id),
            ("TYPE", locked_target.type),
            ("ALTITUDE", f"{locked_target.altitude} FT"),
            ("SPEED", f"{locked_target.speed} KM/H"),
            ("HEADING", f"{int(locked_target.heading)}°"),
            ("DISTANCE", f"{int(locked_target.distance)} PX"),
            ("AI SCORE", f"{locked_target.threat_score}%"),
            ("AI INTENT", locked_target.intent),
            ("THREAT", locked_target.threat)

        ]

        y = panel_y + 82

        for label, value in info:

            color = GREEN

            if label == "THREAT":

                if value == "HIGH":
                    color = RED

                elif value == "MEDIUM":
                    color = (255, 255, 0)

            text = info_font.render(
                f"{label:<12}: {value}",
                True,
                color
            )

            screen.blit(
                text,
                (panel_x + 10, y)
            )

            y += 24

        pygame.draw.line(
            screen,
            DARK_GREEN,
            (panel_x + 10, panel_y + 285),
            (panel_x + 235, panel_y + 285),
            2
        )

        title = info_font.render(
            "AI RECOMMENDATION",
            True,
            LIGHT_GREEN
        )

        screen.blit(
            title,
            (panel_x + 10, panel_y + 270)
        )

        for j, recommendation in enumerate(recommendations):
            text = info_font.render(
                "✔ " + recommendation,
                True,
                GREEN
            )

            screen.blit(
                text,
                (
                    panel_x + 10,
                    panel_y + 295 + j * 22
                )
            )

        pygame.draw.line(
            screen,
            DARK_GREEN,
            (panel_x + 10, panel_y + 390),
            (panel_x + 235, panel_y + 390),
            2
        )

        status_title = info_font.render(
            "SYSTEM STATUS",
            True,
            LIGHT_GREEN
        )

        screen.blit(
            status_title,
            (panel_x + 10, panel_y + 398)
        )

        status_lines = [
            "RADAR : ONLINE",
            "CAMERA : ACTIVE",
            "AI ENGINE : RUNNING",
            "SENSOR FUSION : ACTIVE"
        ]

        for i, status in enumerate(status_lines):
            txt = info_font.render(
                status,
                True,
                GREEN
            )

            screen.blit(
                txt,
                (
                    panel_x + 10,
                    panel_y + 425 + i * 18
                )
            )

        # AI Threat Meter

        bar_x = panel_x + 10
        bar_y = panel_y + 215

        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (panel_x, panel_y, 250, 420),
            2
        )

        fill_width = int((locked_target.threat_score / 100) * 200)

        if locked_target.threat_score >= 80:
            bar_color = RED
        elif locked_target.threat_score >= 50:
            bar_color = (255, 255, 0)
        else:
            bar_color = GREEN

        pygame.draw.rect(
            screen,
            bar_color,
            (bar_x, bar_y, fill_width, 18)
        )

        score_text = info_font.render(
            f"AI THREAT : {locked_target.threat_score}%",
            True,
            bar_color
        )

        screen.blit(
            score_text,
            (bar_x, bar_y + 25)
        )

        pygame.draw.line(
            screen,
            DARK_GREEN,
            (panel_x + 10, panel_y + 255),
            (panel_x + 235, panel_y + 255),
            2
        )

    if collision_warning:
        warning = font.render(
            "COLLISION WARNING",
            True,
            RED
        )

        ids = small_font.render(
            collision_text,
            True,
            RED
        )

        screen.blit(
            warning,
            (20, 20)
        )

        screen.blit(
            ids,
            (20, 50)
        )

    if explosion_active:

        for particle in explosion_particles[:]:

            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]

            particle["life"] -= 1

            pygame.draw.circle(
                screen,
                (255, 180, 0),
                (int(particle["x"]), int(particle["y"])),
                3
            )

            if particle["life"] <= 0:
                explosion_particles.remove(particle)

        pygame.draw.circle(
            screen,
            (255, 120, 0),
            (int(explosion_x), int(explosion_y)),
            explosion_radius
        )

        explosion_radius += 2

        if explosion_radius > 30:
            explosion_active = False
            explosion_radius = 5
            explosion_particles.clear()

    if frame is not None:

        cv2.imshow("AegisAI Vision", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            running = False

    pygame.display.flip()
    clock.tick(FPS)

vision.release()
pygame.quit()