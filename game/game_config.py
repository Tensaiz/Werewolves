import json


class GameConfig():
    def __init__(self):
        self.number_of_werewolves = "auto"

        self.hide_deaths = False
        self.seer_role = False
        self.witch_role = False
        self.hunter_role = False
        self.innocent_role = False
        self.cupid_role = False

        self.base_round_time = 6
        self.werewolf_round_time = 6
        self.role_decide_time = 6
        self.transition_time = 2

    def set(self, variable, value):
        if hasattr(self, variable):
            setattr(self, variable, value)

    def get(self, variable):
        if hasattr(self, variable):
            return getattr(self, variable)
        return None

    def load_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        for k in data:
            v = data[k]
            if hasattr(self, k):
                setattr(self, k, v)

    def to_json(self):
        return json.dumps(self.__dict__)
