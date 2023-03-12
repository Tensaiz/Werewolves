from typing import List

from game.player import Player


class Message():
    def __init__(
            self,
            action: str,
            players: List[Player] = None,
            id: int = None,
            result: int = None,
            votee: str = None,
            base_round_time=-1,
            werewolf_round_time=-1,
            transition_time=-1,
            role_decide_time=-1,
            winner=-1,
            is_host=False,
            config={}
    ):
        self.action = action
        self.players = players
        self.id = id
        self.result = result
        self.votee = votee
        self.base_round_time = base_round_time
        self.werewolf_round_time = werewolf_round_time
        self.transition_time = transition_time
        self.role_decide_time = role_decide_time
        self.winner = winner
        self.is_host = is_host
        self.config = config

    def __str__(self):
        return vars(self)
    