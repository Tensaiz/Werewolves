import json
from typing import List
from game.authentication_ui import AuthenticationUI

from game.ui import UI
from network.client import WerewolfNetworkClient
from game.player import Player
from game.utils import Utils
from game.message import Message


class WerewolfClientController():
    def __init__(self, network_client: WerewolfNetworkClient = None):
        self.MIN_PLAYERS = 1

        self.player = Player("Test")
        self.players = []
        self.ui = UI(self)
        self.auth_ui = AuthenticationUI(self)
        self.network_client = None

        self.round_timer = None
        self.werewolf_timer = None

        self.round_time = -1
        self.wolves_time = -1

        self.base_round_time = -1
        self.werewolf_round_time = -1
        self.transition_time = -1

    def set_networkclient(self, network_client: WerewolfNetworkClient):
        self.network_client = network_client

    def start_auth_ui(self):
        self.auth_ui.mainloop()

    def stop_auth_ui(self):
        self.auth_ui.destroy()

    def start_ui(self):
        self.ui.mainloop()

    def stop_ui(self):
        self.ui.quit()

    def connect(self, name, ip, port):
        self.create_network_client(ip, port)
        self.register_player(name)
        self.stop_auth_ui()
        self.start_ui()

    def create_network_client(self, ip, port):
        self.network_client = WerewolfNetworkClient(ip, int(port))
        self.network_client.set_controller(self)
        self.network_client.connect()
        self.network_client.run()

    def register_player(self, name):
        message = {
            'action': 'REGISTER_PLAYER',
            'name': name
        }
        self.send_message(message)

    def dict_to_json(self, d):
        return json.dumps(d)

    def disconnect(self):
        pass

    def send_message(self, json_msg):
        self.network_client.send_message(self.dict_to_json(json_msg))

    def start_game(self):
        start_game_json = {
            'action': 'START_GAME'
        }
        self.send_message(start_game_json)

    def handle_message(self, message):
        message = Message(message)
        if message.action == "START_GAME":
            self.start_game_server(message)
        elif message.action == "REGISTER_PLAYER":
            # receive id: [id]
            self.set_id(message)
        elif message.action == "PREGAME_OVERVIEW":
            # players: dict[] w/ keys id, name
            self.update_pregame_lobby(message)
        elif message.action == "FINISH_BASE_VOTE":
            # action, result (1 decisive, else 0), votee (votee name)
            # players
            self.handle_base_vote_finish(message)
        elif message.action == "FINISH_WEREWOLF_VOTE":
            # action, result (1 decisive, else 0), votee (votee name)
            # players
            self.handle_werewolf_vote(message)
        elif message.action == "FINISH_GAME":
            # winner: 0 -> villager, 1 -> werewolf
            # Players list
            self.finalize_game_ui(message)
            return
        self.ui.update_window()

    def start_game_server(self, message):
        self.ui.is_pregame_lobby = False
        self.update_players(message)

        self.base_round_time = message.base_round_time
        self.werewolf_round_time = message.werewolf_round_time
        self.transition_time = message.transition_time

        self.ui.purge_pregame_widgets()
        self.start_game_progress()

    def start_game_progress(self):
        self.round_time = self.base_round_time
        self.ui.after(1000, self.update_time)

    def update_time(self):
        self.round_time -= 1
        if self.ui.timer_label:
            self.ui.timer_label.configure(text=self.round_time)
        self.ui.after(1000, self.update_time)

    def day_round(self):
        pass

    def night_round(self):
        pass

    def set_id(self, message):
        self.player.id = message.id

    def update_pregame_lobby(self, message):
        self.players = []
        for d in message.players:
            self.players.append(Player(name=d['name'], id=d['id']))

    def update_players(self, message):
        self.find_self_and_update(message.players)
        self.players = []
        for player in message.players:
            self.players.append(Player(dict_obj=player))

    def find_self_and_update(self, players: List[dict]):
        player = Utils.get_player_by_id(self.player.id, players)
        player = Player(dict_obj=player)
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
        self.network_client.update_deafened(deafened)

    def update_muted(self, muted):
        self.ui.update_muted(muted)
        self.network_client.update_muted(muted)

    def handle_base_vote_finish(self, message):
        # todo handle vote
        self.update_players(message)
        self.night()

    def night(self):
        self.ui.update_day_state(False)

    def handle_werewolf_vote(self, message):
        # todo handle vote
        self.update_players(message)

    def finalize_game_ui(self, message):
        if message.winner == 0:
            self.ui.villagers_win()
        elif message.winner == 1:
            self.ui.werewolves_win()

    def vote_player(self, player_id):
        if self.phase == 0:
            vote = 'BASE_VOTE'
        elif self.phase == 2:
            vote = 'WEREWOLF_VOTE'
        message = {
            'action': vote,
            'sender_id': self.player.id,
            'selected_player_id': player_id
        }
        self.send_message(message)
