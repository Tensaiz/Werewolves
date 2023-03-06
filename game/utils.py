import random
from typing import List
from game.player import Player


class Utils:
    @staticmethod
    def get_random_player(players):
        return random.choice(players)

    @staticmethod
    def calculate_available_role_frequency(player_n, roles):
        pass

    @staticmethod
    def get_player_by_id(id, players: List[Player]):
        for player in players:
            if player.id == id:
                return player
