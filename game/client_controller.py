import json
from game.authentication_ui import AuthenticationUI
from threading import Timer
from game.role import Role
from game.ui import UI
from network.client import WerewolfNetworkClient
from game.player import Player
from game.message import Message
from network.game_progression import GameProgression

MIN_PLAYERS = 1


class WerewolfClientController():
    def __init__(self):
        self.game_is_finished = False

        self.player = Player()
        self.players = []
        self.is_player_host = False

        self.round = 0
        self.phase = 'Civilians voting'
        self.base_round_time = -1
        self.werewolf_round_time = -1
        self.transition_time = -1
        self.role_decide_time = -1

        self.ui = UI(self)
        self.ui.iconbitmap(default="resources/werewolves_icon.ico")
        self.auth_ui = AuthenticationUI(self)
        self.network_client = None

        self.next_rounds = []

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
        message = Message(**message)
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
        elif message.action == "FINISH_WITCH_VOTE":
            self.handle_witch_vote(message)
        elif message.action == "FINISH_GAME":
            # winner: 0 -> villager, 1 -> werewolf
            # Players list
            self.phase = 'Game finished'
            self.game_is_finished = True
            self.finalize_game_ui(message)
            return
        self.ui.update_window()

    def start_game_server(self, message):
        self.ui.is_pregame_lobby = False
        self.reset()

        self.update_players(message)

        self.base_round_time = message.base_round_time
        self.werewolf_round_time = message.werewolf_round_time
        self.transition_time = message.transition_time

        self.ui.purge_pregame_widgets()
        self.ui.after(100, lambda: self.ui.update_timer(self.base_round_time))

    def set_id(self, message):
        self.player.id = message.id
        self.is_player_host = message.is_host

    def update_pregame_lobby(self, message):
        self.players = []
        for d in message.players:
            self.players.append(Player(name=d['name'], id=d['id']))

    def update_players(self, message):
        self.players = []
        for player_dict in message.players:
            player = Player(**player_dict)
            if player.id == self.player.id:
                self.compare_and_update_own_state(player)
            self.players.append(player)

    def compare_and_update_own_state(self, player: Player):
        if self.player.is_alive != player.is_alive:
            self.update_living(player.is_alive)
        if self.player.is_deafened != player.is_deafened:
            self.update_deafened(player.is_deafened)
        if self.player.is_muted != player.is_muted:
            self.update_muted(player.is_muted)
        self.player = player

    def update_living(self, is_alive):
        self.ui.update_living(is_alive)

    def update_deafened(self, deafened):
        self.ui.update_deafened(deafened)
        self.network_client.update_deafened(deafened)

    def update_muted(self, muted):
        self.ui.update_muted(muted)
        self.network_client.update_muted(muted)

    def handle_base_vote_finish(self, message):
        self.update_players(message)
        self.phase = 'Transitioning...'
        self.remove_voting_ui()

        self.next_rounds = GameProgression.get_phases(self.players)
        self.transition_to_next_night_round()

    def transition_to_next_night_round(self):
        # Seer round
        if 0 in self.next_rounds:
            self.next_rounds.remove(0)
            role_round = self.seer_round
        # Werewolves round
        elif 1 in self.next_rounds:
            self.next_rounds.remove(1)
            role_round = self.werewolves_voting
        # Witch round
        elif 2 in self.next_rounds:
            self.next_rounds.remove(2)
            role_round = self.witch_round
        else:
            self.ui.update_window()
            role_round = self.reset_round

        self.ui.update_timer(self.transition_time)
        transition_timer = Timer(self.transition_time, role_round)
        transition_timer.start()

    def werewolves_voting(self):
        if self.phase == 'Game finished':
            return

        self.phase = 'Werewolves eating'

        self.ui.update_timer(self.werewolf_round_time)
        self.ui.update_window()

    def seer_round(self):
        self.phase = 'Seer peeking'

        self.ui.update_timer(self.role_decide_time)
        self.ui.update_window()

        transition_timer = Timer(self.role_decide_time, self.update_and_next_night_round)
        transition_timer.start()


    def update_and_next_night_round(self):
        self.ui.update_window()
        self.transition_to_next_night_round()


    def witch_round(self):
        self.phase = 'Witch healing or poisoning'

        self.ui.update_timer(self.role_decide_time) # add correct round time
        self.ui.update_window()

        transition_timer = Timer(self.role_decide_time, self.transition_to_next_night_round)
        transition_timer.start()

    def reset_round(self):
        self.round += 1
        self.phase = 'Civilians voting'
        self.ui.update_window()
        self.ui.update_timer(self.base_round_time)

    def handle_werewolf_vote(self, message):
        self.werewolf_votee = message.votee
        self.handle_night_vote(message)

    def handle_witch_vote(self, message):
        self.handle_night_vote(message)

    def handle_night_vote(self, message):
        self.update_players(message)
        self.phase = 'Transitioning'
        self.remove_voting_ui()
        self.transition_to_next_night_round()

    def remove_voting_ui(self):
        self.ui.remove_voting_marks()

    def finalize_game_ui(self, message):
        self.unmute_all_players()
        self.ui.update_window()
        self.ui.show_final_game_ui(message.winner)

    def unmute_all_players(self):
        self.update_muted(False)
        self.update_deafened(False)
        for player in self.players:
            player.is_muted = False
            player.is_deafened = False

    def find_self_and_update(self, players):
        for player in players:
            if player.id == self.player.id:
                self.compare_and_update_own_state(player)

    def can_vote_on(self, votee):
        if not (self.player.is_alive and votee.is_alive and votee.id != self.player.id and not self.game_is_finished):
            return False
        # Everyone during voting day
        if self.phase == 'Civilians voting':
            return True
        # Werewolf at night
        if self.phase == 'Werewolves eating' and self.player.role.id == 1:
            return True
        return False

    def sees_role_of(self, player):
        if hasattr(player, 'role') and player.role is not None:
            if self.game_is_finished:
                role = Role.get_role_name_from_id(player.role.id).lower()
            elif player.role.id == 1 and self.player.role.id == 1:
                role = Role.get_role_name_from_id(player.role.id).lower()
            elif not player.is_alive:
                role = Role.get_role_name_from_id(player.role.id).lower()
            elif player.id == self.player.id:
                role = Role.get_role_name_from_id(player.role.id).lower()
            else:
                role = 'unknown'
        else:
            role = 'unknown'
        return role

    def vote_player(self, player_id):
        if self.phase == 'Civilians voting':
            vote = 'BASE_VOTE'
        elif self.phase == 'Werewolves eating':
            vote = 'WEREWOLF_VOTE'
        message = {
            'action': vote,
            'sender_id': self.player.id,
            'selected_player_id': player_id
        }
        self.send_message(message)

    def restart_game(self):
        self.send_message(
            {'action': 'NEW_GAME'}
        )

    def reset(self):
        self.game_is_finished = False
        self.round = 0
        self.phase = 'Civilians voting'
        self.ui.reset_for_next_game()
