class CommandCenter:

    def recommend(self, aircraft):

        if aircraft.threat == "HIGH":

            return [
                "LOCK TARGET",
                "TRACK CONTINUOUSLY",
                "PREPARE MISSILE",
                "INTERCEPT ADVISED"
            ]

        elif aircraft.threat == "MEDIUM":

            return [
                "MONITOR TARGET",
                "CONTINUE TRACKING",
                "IDENTIFY OBJECT"
            ]

        else:

            return [
                "NO ACTION REQUIRED",
                "PASSIVE MONITORING"
            ]