class Role:
    def __init__(self, role_id, **kwargs):
        self.id = role_id
        self.name = self.get_role_name_from_id(self.id)
        self.in_love_with = kwargs.get('in_love_with', -1)

    def __str__(self) -> str:
        return f'{self.id} - {self.name}'

    @staticmethod
    def get_role_priority(role_id):
        role_priority_dict = {
            0: 5,
            1: 4,
            2: 1,
            3: 2,
            4: 5,
            5: 0,
            6: 5
        }
        return role_priority_dict[role_id]

    @staticmethod
    def get_role_name_from_id(role_id):
        role_name_dict = {
            0: 'Villager',
            1: 'Werewolf',
            2: 'Witch',
            3: 'Hunter',
            4: 'Seer',
            5: 'Cupid',
            6: 'Innocent'
        }
        return role_name_dict[role_id]

    @staticmethod
    def get_role_class_from_id(role_id):
        role_class_dict = {
            0: Villager,
            1: Werewolf,
            2: Witch,
            3: Hunter,
            4: Seer,
            5: Cupid,
            6: Innocent
        }
        return role_class_dict[role_id]

    @staticmethod
    def get_players_by_role(players, role_id):
        players_with_role = []
        for player in players:
            if player.role.id == role_id:
                players_with_role.append(player)
        return players_with_role


class Villager(Role):
    def __init__(self, **kwargs):
        self.id = 0
        super().__init__(self.id, **kwargs)


class Werewolf(Role):
    def __init__(self, **kwargs):
        self.id = 1
        super().__init__(self.id, **kwargs)


class Witch(Role):
    def __init__(self, has_healing_potion=1, has_killing_potion=1, **kwargs):
        self.id = 2
        super().__init__(self.id, **kwargs)
        self.has_healing_potion = has_healing_potion
        self.has_killing_potion = has_killing_potion


class Hunter(Role):
    def __init__(self, bullet=1, **kwargs):
        self.id = 3
        super().__init__(self.id, **kwargs)
        self.bullet = bullet


class Seer(Role):
    def __init__(self, **kwargs):
        self.id = 4
        super().__init__(self.id, **kwargs)


class Cupid(Role):
    def __init__(self, **kwargs):
        self.id = 5
        super().__init__(self.id, **kwargs)


class Innocent(Role):
    def __init__(self, **kwargs):
        self.id = 6
        super().__init__(self.id, **kwargs)
