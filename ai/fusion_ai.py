class SensorFusion:

    def __init__(self):
        self.targets = []

    def fuse(self, enemies, detections):
        """
        Fuse radar targets with vision detections.
        """

        self.targets = detections

        for enemy in enemies:

            enemy.detected = False

            for detection in detections:

                dx = enemy.x - detection["center_x"]
                dy = enemy.y - detection["center_y"]

                if dx * dx + dy * dy < 50 * 50:
                    enemy.detected = True

    def get_targets(self):
        return self.targets