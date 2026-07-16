class ThreatEngine:

    def __init__(self):
        pass

    def evaluate(self, track):

        if track.name == "person":

            track.threat = "MEDIUM"

            track.confidence = 95

        elif track.name in [

            "knife",

            "gun",

            "scissors"

        ]:

            track.threat = "HIGH"

            track.confidence = 100

        else:

            track.threat = "LOW"

            track.confidence = 80

        return track