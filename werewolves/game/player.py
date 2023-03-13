from werewolves.game.role import Role


class Player():
    def __init__(self, name='', client=None, dict_obj=None, id=-1, role=None, is_alive=True, is_muted=False, is_deafened=False):
        self.id = id
        self.name = name
        self.client = client

        if role:
            role_id = role['id']
            self.role = Role.get_role_class_from_id(role_id)(**role)
        else:
            self.role = None

        self.is_alive = is_alive
        self.is_muted = is_muted
        self.is_deafened = is_deafened

    def reset(self):
        self.role = None
        self.is_alive = True
        self.is_muted = False
        self.is_deafened = False

    def __str__(self):
        return f'''
{self.name}
{self.role}
{self.is_alive}
{self.is_muted}
{self.is_deafened}
        '''
