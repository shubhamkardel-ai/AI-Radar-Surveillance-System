import pygame


class PanelRenderer:

    def __init__(self):
        pass

    def draw_track_panel(
        self,
        screen,
        track,
        font,
        small_font,
        width,
        green,
        light_green
    ):

        pygame.draw.rect(
            screen,
            (15, 15, 15),
            (width - 270, 100, 250, 180)
        )

        pygame.draw.rect(
            screen,
            green,
            (width - 270, 100, 250, 180),
            2
        )

        title = font.render(
            "TRACK INFORMATION",
            True,
            green
        )

        screen.blit(
            title,
            (width - 255, 110)
        )

        info = [

            f"ID : TRACK-{track.id:03}",

            f"OBJECT : {track.name.upper()}",

            f"THREAT : {track.threat}",

            f"SEEN : {track.time_seen}",

            f"CONFIDENCE : {track.confidence}%"

        ]

        y = 145

        for line in info:

            txt = small_font.render(
                line,
                True,
                light_green
            )

            screen.blit(
                txt,
                (width - 255, y)
            )

            y += 25