class Player:
    def __init__(self, name):
        self.name = name
        self.role = None
        self.is_alive = True

    def reset(self):
        self.role = None
        self.is_alive = True
