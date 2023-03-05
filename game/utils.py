import random
from typing import List

from game.player import Player
from game.role import Role


class Utils:
    @staticmethod
    def get_random_player(players):
        return random.choice(players)

    @staticmethod
    def assign_roles(players: List[Player], roles: List[Role]):
        num_players = len(players)
        num_roles = len(roles)
        if num_roles < num_players:
            raise ValueError('Not enough roles for all players')
        random.shuffle(roles)
        for i in range(num_players):
            players[i].role = roles[i]

    @staticmethod
    def calculate_available_role_frequency(player_n, roles):
        pass

    @staticmethod
    def get_player_by_id(id, players: List[Player]):
        for player in players:
            if player['id'] == id:
                return player
