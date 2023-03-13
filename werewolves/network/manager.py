import json
import collections
from typing import List
from threading import Timer
import time
import uuid
import random
from werewolves.game.player import Player
from werewolves.game.role import Role
from werewolves.game.config import Config


class Manager():
    def __init__(self, server) -> None:
        self.base_votes = [{}]
        self.werewolf_votes = [{}]
        self.witch_votes = {}
        self.hunter_votee = None
        self.hunter_killed = False
        self.round = 0
        self.server = server
        self.round_timer = None
        self.players: List[Player] = []
        self.config: Config = Config()

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
        elif message["action"] == "WITCH_VOTE":
            self.witch_vote(message)
        elif message["action"] == "HUNTER_VOTE":
            self.hunter_vote(message)
        elif message["action"] == "UPDATE_CONFIG":
            self.update_config(message)
        elif message["action"] == "NEW_GAME":
            self.restart()

    def update_config(self, update):
        cfg = update["config"]
        self.config.load_json(cfg)

    def restart(self):
        self.base_votes = [{}]
        self.werewolf_votes = [{}]
        self.witch_votes = {}
        self.hunter_votee = None
        self.hunter_killed = False
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
        player = Player(name=player_name, id=player_id, client=sender)
        self.players.append(player)
        sender.send({
            "action": "REGISTER_PLAYER",
            "id": player_id,
            "is_host": len(self.players) == 1
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
                "config": self.config.to_json()
            })

        if self.game_finished():
            return

        if self.hunter_killed:
            self.hunter_round()
            self.hunter_killed = False

        self.round_timer = Timer(self.config.base_round_time, lambda: self.finish_voting("base"))
        self.round_timer.start()

    '''
    Return phase ids of the roles that have a turn during the night based on the player list argument
    0 = seer
    1  = werewolves
    2 = witch
    '''
    @staticmethod
    def get_phases(players):
        # 0 - Seer -> 1 - werewolves -> 2 - witch
        phases = []
        for player in players:
            if not player.is_alive:
                continue
            elif player.role.id == 4:
                # Seer turn this round
                phases.append(0)
            elif player.role.id == 1 and 1 not in phases:
                # Werewolves turn
                phases.append(1)
            elif player.role.id == 2 and (player.role.has_healing_potion or player.role.has_killing_potion):
                # Witch turn
                phases.append(2)
        return phases

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
        werewolf_count = len(list(filter(lambda x: x.role.id == 1, alive_players)))
        villager_count = len(list(filter(lambda x: x.role.id != 1, alive_players)))

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

    def witch_vote(self, message):
        if "save" in message.keys():
            self.witch_votes["save"] = message["save"]
        elif "kill" in message.keys():
            self.witch_votes["kill"] = message["kill"]

    def hunter_vote(self, message):
        self.hunter_votee = message["selected_player_id"]

    def finish_voting(self, type: str):
        self.round_timer = None
        votee = self.calculate_votee(type)

        night_rounds = self.get_phases(self.players)

        # Process dead player
        if votee and type in ["base", "werewolf"]:
            self.kill_player(votee)

        # Don't change player audio if the witch still has its turn
        if not (type == "werewolf" and 2 in night_rounds):
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

        # Don't change player audio if the witch still has its turn
        if not (type == "werewolf" and 2 in night_rounds):
            if self.game_finished():
                return

        # Transition to next phase
        if type == "base":
            # Transition to next night voting phase
            time.sleep(self.config.transition_time)

            if self.hunter_killed:
                # Hunter turn
                self.hunter_round()

            # Wait for Seer to view a role on client side
            if 0 in night_rounds:
                time.sleep(self.config.role_decide_time + self.config.transition_time)

            # Start calculating werewolf votes after werewolf round time
            werewolf_timer = Timer(self.config.werewolf_round_time, lambda: self.finish_voting("werewolf"))
            werewolf_timer.start()
        elif type == "werewolf":
            time.sleep(self.config.transition_time)
            self.round += 1
            self.base_votes.append({})
            self.werewolf_votes.append({})

            if 2 in night_rounds:
                # Witch turn
                witch_timer = Timer(self.config.role_decide_time, lambda: self.finish_witch_voting())
                witch_timer.start()
            else:
                # Update player muted status and broadcast
                self.start_round()

    def hunter_round(self):
        hunter_timer = Timer(self.config.role_decide_time, lambda: self.finish_hunter_voting())
        hunter_timer.start()

    def finish_witch_voting(self):
        time.sleep(self.config.transition_time)

        witch_player = Role.get_players_by_role(self.players, 2)[0]

        for key in list(self.witch_votes.keys()):
            if key == "save":
                # Save player and remove life potion
                self.revive_player(self.witch_votes["save"])
                witch_player.role.has_healing_potion = 0
            elif key == "kill":
                # Kill another player and remove poison
                self.kill_player(self.witch_votes["kill"])
                witch_player.role.has_killing_potion = 0

        if self.game_finished():
            return

        self.change_player_audio(False)

        # Send latest player update
        action_name = "FINISH_WITCH_VOTE"
        self.server.broadcast({
            "action": action_name,
            "players": self.map_players()
        })
        self.start_round()

    def finish_hunter_voting(self):
        time.sleep(self.config.transition_time)

        if not self.hunter_votee:
            return

        hunter_player = Role.get_players_by_role(self.players, 3)[0]
        hunter_player.role.bullet = 0
        self.kill_player(self.hunter_votee)

        if self.game_finished():
            return

        action_name = "FINISH_HUNTER_VOTE"
        self.server.broadcast({
            "action": action_name,
            "players": self.map_players()
        })

    def change_player_audio(self, mute):
        for player in self.players:
            if player.role.id != 1:
                player.is_deafened = mute if player.is_alive else False
                player.is_muted = mute
            if not player.is_alive:
                player.is_muted = True

    def revive_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                player.is_alive = True
                break

    def kill_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                if player.role.id == 3:
                    self.hunter_killed = True
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
        if self.config.number_of_werewolves == "auto":
            no_of_werewolves = len(self.players) // 4
        else:
            no_of_werewolves = int(self.config.number_of_werewolves)
        no_of_seer = self.config.seer_role
        no_of_hunter = self.config.hunter_role
        no_of_inno = self.config.innocent_role
        no_of_witch = self.config.witch_role
        no_of_cupid = self.config.cupid_role
        no_of_alternates = no_of_seer + no_of_hunter + no_of_inno + no_of_witch + no_of_cupid
        no_of_villagers = len(self.players) - no_of_werewolves - no_of_alternates

        role_assignment = [0] * no_of_villagers + [1] * no_of_werewolves
        role_assignment += [2] * no_of_witch
        role_assignment += [3] * no_of_hunter
        role_assignment += [4] * no_of_seer
        role_assignment += [5] * no_of_cupid
        role_assignment += [6] * no_of_inno

        random.shuffle(role_assignment)

        for i, player in enumerate(self.players):
            id = role_assignment[i]
            player.role = Role.get_role_class_from_id(id)()

    def map_players(self):
        return list(map(lambda x: {
            "name": x.name,
            "id": x.id,
            "role": vars(x.role),
            "is_alive": x.is_alive,
            "is_muted": x.is_muted,
            "is_deafened": x.is_deafened
        }, self.players))

    def map_pregame_players(self):
        return list(map(lambda x: {
            "name": x.name,
            "id": x.id
        }, self.players))
