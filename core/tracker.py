import math


class Track:

    def __init__(self, track_id, x, y, name):

        self.id = track_id

        self.x = x
        self.y = y

        self.name = name

        self.age = 0

        self.missed = 0

        self.history = []

        self.confidence = 100

        self.threat = "LOW"

        self.time_seen = 0

    def update(self, x, y):

        self.x = x
        self.y = y

        self.age += 1

        self.missed = 0

        self.time_seen += 1

        self.history.append((x, y))

        if len(self.history) > 40:
            self.history.pop(0)


class Tracker:

    def __init__(self):

        self.tracks = []

        self.next_id = 1

    def create_track(self, x, y, name):

        for track in self.tracks:

            distance = math.sqrt(

                (track.x - x) ** 2 +

                (track.y - y) ** 2

            )

            if distance < 180:
                track.update(x, y)

                return

        track = Track(

            self.next_id,

            x,

            y,

            name

        )

        self.tracks.append(track)

        self.next_id += 1

    def get_tracks(self):

        return self.tracks

    def update_tracks(self):

        alive_tracks = []

        for track in self.tracks:

            track.missed += 1

            if track.missed < 20:
                alive_tracks.append(track)

        self.tracks = alive_tracks