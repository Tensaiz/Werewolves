class Player():
    def __init__(self, name='', dict_obj=None, id=-1, role=None, is_alive=True, is_muted=False, is_deafened=False):
        if dict_obj:
            for key in dict_obj:
                setattr(self, key, dict_obj[key])
        else:
            self.id = id
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

    def __str__(self):
        return f'''
{self.name}
{self.role}
{self.is_alive}
{self.is_muted}
{self.is_deafened}
        '''
