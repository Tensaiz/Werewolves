import json
import collections
from typing import List
from threading import Timer
import time
import uuid
import random

"""
Game agenda

0 Discussion + voting: x secs

1 Mini-transition: 3 secs

Announcement base vote

Transition: 5 secs

2 Werewolf voting: y secs

3 Transition: 5 secs

Announcement werewolf vote

Mini-transition: 3 secs
"""

"""
Roles
0: villager
1: werewolf
"""


class Player():
    def __init__(self, name, id, client) -> None:
        self.name = name
        self.id = id
        self.client = client
        self.role = None
        self.is_alive = True
        self.is_muted = False
        self.is_deafened = False


class GameProgression():
    def __init__(self, server) -> None:
        self.base_votes = [{}]
        self.werewolf_votes = [{}]
        self.round = 0
        self.base_round_time = 5
        self.werewolf_round_time = 5
        self.transition_time = 8
        self.server = server
        self.round_timer = None
        self.players: List[Player] = []

    def process(self, message, sender):
        message = json.loads(message.decode('utf-8'))

        if message["action"] == "REGISTER_PLAYER":
            self.register_player(message, sender)
        elif message["action"] == "START_GAME":
            self.start_round()
        elif message["action"] == "BASE_VOTE":
            self.vote("base", message)
        elif message["action"] == "WEREWOLF_VOTE":
            self.vote("werewolf", message)
        elif message["action"] == "NEW_GAME":
            self.restart()

    def restart(self):
        self.base_votes = [{}]
        self.werewolf_votes = [{}]
        self.round = 0
        self.round_timer = None

        for player in self.players:
            player.is_alive = True
            player.is_muted = False
            player.is_deafened = False

        self.start_round()

    def register_player(self, message, sender):
        player_name = message["name"]
        player_id = str(uuid.uuid4())
        player = Player(player_name, player_id, sender)
        self.players.append(player)
        sender.send({
            "action": "REGISTER_PLAYER",
            "id": player_id
        })

        self.server.broadcast({
            "action": "PREGAME_OVERVIEW",
            "players": self.map_pregame_players()
        })

    def remove_player(self, client):
        removable = None
        for p in self.players:
            if p.client == client:
                removable = p
                break
        if removable is not None:
            self.players.remove(p)

        self.server.broadcast({
            "action": "PREGAME_OVERVIEW",
            "players": self.map_pregame_players()
        })

    def start_round(self):
        if self.round_timer:
            return

        if self.round == 0:
            # Start of the game, assign roles, send players
            self.assign_roles()
            self.server.broadcast({
                "action": "START_GAME",
                "players": self.map_players(),
                "base_round_time": self.base_round_time,
                "werewolf_round_time": self.werewolf_round_time,
                "transition_time": self.transition_time
            })

        if self.game_finished():
            return

        self.round_timer = Timer(self.base_round_time, lambda: self.finish_voting("base"))
        self.round_timer.start()

    def game_finished(self):
        winner = self.calculate_winners()
        if winner >= 0:
            self.server.broadcast({
                "action": "FINISH_GAME",
                "winner": winner,
                "players": self.map_players()
            })
            return True
        return False

    def calculate_winners(self):
        alive_players = list(filter(lambda x: x.is_alive, self.players))
        werewolf_count = len(list(filter(lambda x: x.role == 1, alive_players)))
        villager_count = len(list(filter(lambda x: x.role == 0, alive_players)))

        if werewolf_count >= villager_count:
            winner = 1
        elif werewolf_count == 0:
            winner = 0
        else:
            winner = -1
        return winner

    def vote(self, type, message):
        sender = message["sender_id"]
        voted_on = message["selected_player_id"]
        if type == "base":
            self.base_votes[self.round][sender] = voted_on
        elif type == "werewolf":
            self.werewolf_votes[self.round][sender] = voted_on

    def finish_voting(self, type: str):
        self.round_timer = None
        votee = self.calculate_votee(type)

        # Process dead player
        if votee and type in ["base", "werewolf"]:
            self.kill_player(votee)
        self.change_player_audio("base" == type)

        # SEND VOTEE TO CLIENTS
        type_upper = type.upper()
        action_name = f"FINISH_{type_upper}_VOTE"
        self.server.broadcast({
            "action": action_name,
            "result": 1 if votee else 0,
            "votee": votee,
            "players": self.map_players()
        })

        if self.game_finished():
            return

        # Transition to next phase
        if type == "base":
            # Transition to werewolf voting phase
            time.sleep(self.transition_time)
            # Update player muted status and broadcast

            werewolf_timer = Timer(self.werewolf_round_time, lambda: self.finish_voting("werewolf"))
            werewolf_timer.start()
        elif type == "werewolf":
            time.sleep(self.transition_time)
            self.round += 1
            self.base_votes.append({})
            self.werewolf_votes.append({})

            # Update player muted status and broadcast
            self.start_round()

    def change_player_audio(self, mute):
        for player in self.players:
            if player.role == 0:
                player.is_deafened = mute if player.is_alive else False
                player.is_muted = mute
            if not player.is_alive:
                player.is_muted = True

    def kill_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                player.is_alive = False
                break

    def calculate_votee(self, type):
        if type == "base":
            votes = self.base_votes[self.round]
        elif type == "werewolf":
            votes = self.werewolf_votes[self.round]

        if len(votes) == 0:
            return False

        counter = collections.Counter(list(votes.values()))
        most_common_amount = 2 if len(counter) > 1 else 1
        most_common = counter.most_common(most_common_amount)
        if most_common_amount == 1:
            return most_common[0][0]
        else:
            if most_common[0][1] == most_common[1][1]:
                return False
            else:
                return most_common[0][0]

    def assign_roles(self):
        amount_of_werewolves = len(self.players) // 4
        amount_of_villagers = len(self.players) - amount_of_werewolves
        role_assignment = [0] * amount_of_villagers + [1] * amount_of_werewolves
        random.shuffle(role_assignment)
        for i, player in enumerate(self.players):
            player.role = role_assignment[i]

    def map_players(self):
        return list(map(lambda x: {
            "name": x.name,
            "id": x.id,
            "role": x.role,
            "is_alive": x.is_alive,
            "is_muted": x.is_muted,
            "is_deafened": x.is_deafened
        }, self.players))

    def map_pregame_players(self):
        return list(map(lambda x: {
            "name": x.name,
            "id": x.id
        }, self.players))
