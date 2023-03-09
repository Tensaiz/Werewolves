class Role:
    def __init__(self, name, role_id):
        self.name = name
        self.id = role_id

    def do_action(self):
        pass

    @staticmethod
    def get_role_name_from_id(id):
        role_name_dict = {
            0: 'Villager',
            1: 'Werewolf'
        }
        return role_name_dict[id]


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
