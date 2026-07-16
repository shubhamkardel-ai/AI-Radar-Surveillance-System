import pygame


class RadarRenderer:

    def __init__(self):
        pass

    def draw_trail(self, screen, track):

        for point in track.history:

            pygame.draw.circle(

                screen,

                (0, 120, 255),

                (int(point[0]), int(point[1])),

                2

            )

    def draw_track(self, screen, track, small_font):

        pygame.draw.circle(

            screen,

            (0, 200, 255),

            (int(track.x), int(track.y)),

            8,

            2

        )

        label = small_font.render(

            f"TRACK-{track.id:03}",

            True,

            (0, 255, 255)

        )

        screen.blit(

            label,

            (

                int(track.x) + 10,

                int(track.y) - 10

            )

        )

    def draw_lock_ring(self, screen, x, y):
        pygame.draw.circle(

            screen,

            (255, 255, 0),

            (int(x), int(y)),

            16,

            2

        )

        pygame.draw.circle(

            screen,

            (255, 255, 0),

            (int(x), int(y)),

            22,

            1

        )