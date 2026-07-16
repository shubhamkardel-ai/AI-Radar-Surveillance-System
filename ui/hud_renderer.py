import pygame


class HUDRenderer:

    def __init__(self):
        pass

    def draw(
        self,
        screen,
        fps,
        target_count,
        font,
        green,
        red
    ):

        fps_text = font.render(
            f"FPS : {int(fps)}",
            True,
            green
        )

        screen.blit(
            fps_text,
            (20, 20)
        )

        target_text = font.render(
            f"TARGETS : {target_count}",
            True,
            green
        )

        screen.blit(
            target_text,
            (20, 50)
        )

        title = font.render(
            "AEGISAI DEFENSE GRID",
            True,
            red
        )

        screen.blit(
            title,
            (170, 30)
        )