import json

from game.ui import UI
from network.client import WerewolfNetworkClient
from game.player import Player
from game.utils import Utils


class WerewolfClientController():
    def __init__(self, client: WerewolfNetworkClient):
        self.networkclient = client
        self.player = Player("Test")
        self.players = []
        self.ui = UI(self)

    def set_networkclient(self, networkclient: WerewolfNetworkClient):
        self.networkclient = networkclient

    def connect(self):
        pass

    def disconnect(self):
        pass

    def send_message(self, json_msg):
        self.client.send_message(json.dumps(json_msg))

    def handle_message(self, message):
        if message.action == "START_GAME":
            # players
            print(message)
        elif message.action == "REGISTERED_PLAYER":
            # receive id: [id]
            self.set_id(message)
            print(message)
        elif message.action == "PREGAME_OVERVIEW":
            # players: dict[] w/ keys id, name
            self.update_pregame_lobby(message)
            print(message)
        elif message.action == "FINISH_BASE_VOTE":
            # action, result (1 decisive, else 0), votee (votee name)
            # players
            self.handle_base_vote(message)
            print(message)
        elif message.action == "FINISH_WEREWOLF_VOTE":
            # action, result (1 decisive, else 0), votee (votee name)
            # players
            self.handle_werewolf_vote(message)
            print(message)
        elif message.action == "FINISH_GAME":
            # winner: 0 -> villager, 1 -> werewolf
            # Players list
            pass

    def set_id(self, message):
        self.player.id = message['id']

    def update_pregame_lobby(self, message):
        self.players = []
        for d in message.players:
            self.players.append(Player(name=d['name'], id=d['id']))

    def update_players(self, message):
        self.find_self_and_update(message.players)
        self.players = message.players

    def find_self_and_update(self, message):
        player = Utils.get_player_by_id(self.player.id, message.players)
        self.compare_and_update_own_state(player)

    def compare_and_update_own_state(self, player: Player):
        if self.player.is_alive != player.is_alive:
            self.update_living()
        if self.player.is_deafened != player.is_deafened:
            self.update_deafened()
        if self.player.is_muted != player.is_muted:
            self.update_muted()
        self.player = player

    def update_living(self, state):
        self.ui.update_living(state)

    def update_deafened(self, deafened):
        self.ui.update_deafened(deafened)
        self.networkclient.update_deafened(deafened)

    def update_muted(self, muted):
        self.ui.update_muted(muted)
        self.networkclient.update_muted(muted)

    def handle_base_vote(self, message):
        pass

    def handle_werewolf_vote(self, message):
        pass
