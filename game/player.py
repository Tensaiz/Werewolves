class Player():
    def __init__(self, name, id=None, role=None, is_alive=True, is_muted=False, is_deafened=False):
        self.id = None
        self.name = name
        self.role = role
        self.is_alive = is_alive
        self.is_muted = is_muted
        self.is_deafened = is_deafened

    def reset(self):
        self.role = None
        self.is_alive = True
        self.is_muted = False
        self.is_deafened = False
