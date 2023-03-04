from typing import List

from game.player import Player


class Message():
    def __init__(self, action: str, players: List[Player] = None, player_id: int = None, result: int = None, votee: str = None):
        self.action = action
        self.players
        self.id = player_id
        self.result = result
        self.votee = votee
