class Role:
    def __init__(self, name):
        self.name = name

    def do_action(self):
        pass


class Villager(Role):
    def __init__(self):
        super().__init__("Villager")


class Werewolf(Role):
    def __init__(self):
        super().__init__("Werewolf")

    def do_action(self):
        pass


class Seer(Role):
    def __init__(self):
        super().__init__("Seer")

    def do_action(self):
        pass
