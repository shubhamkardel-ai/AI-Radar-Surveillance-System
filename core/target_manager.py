from aircraft import Aircraft


class TargetManager:

    def __init__(self):
        self.targets = []

    def add_target(self, target):
        self.targets.append(target)

    def remove_target(self, target):
        if target in self.targets:
            self.targets.remove(target)

    def clear(self):
        self.targets.clear()

    def get_targets(self):
        return self.targets