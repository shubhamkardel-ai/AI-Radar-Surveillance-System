import pygame


class MissionRenderer:

    def __init__(self):
        pass

    def draw_mission_log(
        self,
        screen,
        mission_log,
        font,
        small_font,
        green,
        dark_green
    ):

        pygame.draw.rect(
            screen,
            dark_green,
            (20, 520, 360, 220)
        )

        pygame.draw.rect(
            screen,
            green,
            (20, 520, 360, 220),
            2
        )

        title = font.render(
            "MISSION LOG",
            True,
            green
        )

        screen.blit(
            title,
            (35, 530)
        )

        y = 565

        for log in mission_log[-7:]:

            txt = small_font.render(
                log,
                True,
                green
            )

            screen.blit(
                txt,
                (35, y)
            )

            y += 24