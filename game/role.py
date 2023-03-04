class Role:
    def __init__(self, name, role_id):
        self.name = name
        self.id = role_id

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
