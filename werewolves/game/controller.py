import json
from werewolves.game.utils import Utils
from werewolves.ui.auth import AuthenticationUI
from threading import Timer
from werewolves.game.role import Role
from werewolves.ui.main import MainUI
from werewolves.network.client import Client
from werewolves.game.player import Player
from werewolves.network.message import Message
from werewolves.network.manager import Manager
from werewolves.game.config import Config

MIN_PLAYERS = 1


class Controller():
    def __init__(self):
        self.game_is_finished = False

        self.player = Player()
        self.players = []
        self.is_player_host = False

        self.round = 0
        self.phase = 0

        self.ui = MainUI(self)
        self.ui.iconbitmap(default="resources/werewolves_icon.ico")
        self.auth_ui = AuthenticationUI(self)
        self.network_client = None
        self.config = Config()
        self.next_rounds = []

    def set_networkclient(self, network_client: Client):
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
        self.network_client = Client(ip, int(port))
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

    def get_phase_name(self, phase):
        phase_names = {
            -1: 'Transitioning...',
            0: 'Civilians voting',
            1: 'Werewolves eating',
            2: 'Seer peeking',
            3: 'Witch healing or poisoning',
            4: 'Hunter taking revenge',
            10: 'Game finished'
        }
        return phase_names[phase]

    def disconnect(self):
        pass

    def send_message(self, json_msg):
        self.network_client.send_message(self.dict_to_json(json_msg))

    def update_config(self):
        self.send_message({
            "action": "UPDATE_CONFIG",
            "config": self.config.to_json()
        })

    def start_game(self):
        start_game_json = {
            'action': 'START_GAME'
        }
        self.send_message(start_game_json)

    def handle_message(self, message):
        message = Message(**message)
        print(message.action)
        if message.action == "START_GAME":
            self.start_game_server(message)
            self.ui.update_window()
        elif message.action == "REGISTER_PLAYER":
            # receive id: [id]
            self.set_id(message)
            self.ui.update_window()
        elif message.action == "PREGAME_OVERVIEW":
            # players: dict[] w/ keys id, name
            self.update_pregame_lobby(message)
            self.ui.update_window()
        elif message.action == "FINISH_BASE_VOTE":
            # action, result (1 decisive, else 0), votee (votee name)
            # players
            self.handle_base_vote_finish(message)
        elif message.action == "FINISH_WEREWOLF_VOTE":
            # action, result (1 decisive, else 0), votee (votee name)
            # players
            self.handle_werewolf_vote(message)
        elif message.action == "FINISH_WITCH_VOTE":
            self.handle_witch_vote_finished(message)
        elif message.action == "FINISH_HUNTER_VOTE":
            self.handle_hunter_vote(message)
        elif message.action == "FINISH_GAME":
            # winner: 0 -> villager, 1 -> werewolf
            # Players list
            self.phase = 10
            self.game_is_finished = True
            self.finalize_game_ui(message)

    def start_game_server(self, message):
        self.ui.is_pregame_lobby = False
        self.reset()

        self.update_players(message)

        self.base_round_time = message.base_round_time
        self.werewolf_round_time = message.werewolf_round_time
        self.transition_time = message.transition_time
        self.role_decide_time = message.role_decide_time
        self.config.load_json(message.config)

        self.ui.purge_pregame_widgets()
        self.ui.after(100, lambda: self.ui.update_timer(self.config.base_round_time))

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

    def mark_player_speaking(self, sender_id):
        # Players can only see each other speaking if they're werewolves or if they're voting as civilians
        if self.phase == 0 or (self.phase == 1 and self.player.role.id == 1 and Utils.get_player_by_id(sender_id).role.id == 1):
            self.ui.mark_player_speaking(sender_id)

    def update_deafened(self, deafened):
        # Innocent never gets deafened
        if self.player.role.id == 6:
            transition_timer = Timer(self.config.transition_time, lambda: self.innocent_undeafen(deafened))
            transition_timer.start()

        self.ui.update_deafened(deafened)
        self.network_client.update_deafened(deafened)

    def innocent_undeafen(self, deafened):
        if deafened:
            self.network_client.apply_effect = True
        else:
            self.network_client.apply_effect = False
        self.ui.update_deafened(False)
        self.network_client.update_deafened(False)

    def update_muted(self, muted):
        self.ui.update_muted(muted)
        self.network_client.update_muted(muted)

    def handle_base_vote_finish(self, message):
        self.phase = -1
        self.remove_voting_ui()
        self.ui.update_window()
        hunter_status = self.hunter_is_alive()
        self.update_players(message)
        # Hunter has died
        if hunter_status != self.hunter_is_alive():
            self.hunter_death_time = 0  # Hunter killed after civ vote
            self.hunter_round()
        else:
            self.next_rounds = Manager.get_phases(self.players)
            self.transition_to_next_night_round()

    def hunter_is_alive(self):
        for player in self.players:
            if player.role.id == 3 and player.is_alive:
                return True
        return False

    def hunter_round(self):
        self.phase = 4
        self.ui.update_timer(self.config.role_decide_time)
        self.ui.update_window()

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
            print('Night over, civ round')
            role_round = self.reset_round

        self.start_transition(role_round)

    def start_transition(self, to_round):
        if self.player.is_alive:
            self.update_deafened(True)
        self.ui.update_timer(self.config.transition_time)
        transition_timer = Timer(self.config.transition_time, to_round)
        transition_timer.start()

    def werewolves_voting(self):
        if self.phase == 10:
            return

        self.phase = 1

        if self.player.role.id == 1:
            self.update_deafened(False)

        self.ui.update_timer(self.config.werewolf_round_time)
        self.ui.update_window()

    def seer_round(self):
        self.phase = 2
        self.ui.update_timer(self.config.role_decide_time)
        self.ui.update_window()

        transition_timer = Timer(self.config.role_decide_time, self.finish_seer_round)
        transition_timer.start()

    def finish_seer_round(self):
        self.remove_voting_ui()
        self.seer_vote = None
        self.phase = -1
        self.ui.update_window()
        self.transition_to_next_night_round()

    def witch_round(self):
        self.phase = 3

        self.ui.update_timer(self.config.role_decide_time)
        self.ui.update_window()
        self.ui.show_witch_ui()

    def reset_round(self):
        self.round += 1
        self.phase = 0
        self.update_deafened(self.player.is_deafened)
        self.ui.update_window()
        self.ui.update_timer(self.config.base_round_time)

    def handle_werewolf_vote(self, message):
        self.werewolf_votee = message.votee
        # If no witch round
        if 2 not in self.next_rounds:
            hunter_status = self.hunter_is_alive()
            self.update_players(message)
            # Hunter has died
            if hunter_status != self.hunter_is_alive():
                self.hunter_death_time = 1  # Hunter killed after civ vote
                self.hunter_round()
                return
        self.handle_night_vote(message)

    def handle_witch_vote_finished(self, message):
        self.handle_night_vote(message)
        self.update_players(message)
        self.ui.remove_witch_ui()
        self.werewolf_votee = -1

    def handle_hunter_vote(self, message):
        self.phase = -1
        self.remove_voting_ui()
        self.update_players(message)
        self.ui.update_window()
        if self.hunter_death_time == 0:
            # Go to night after hunter was killed after civ vote
            self.next_rounds = Manager.get_phases(self.players)
            self.transition_to_next_night_round()
        else:
            # Go to civilian vote after hunter was killed at night
            self.ui.update_timer(self.config.transition_time)
            transition_timer = Timer(self.config.transition_time, self.reset_round)
            transition_timer.start()

    def handle_night_vote(self, message):
        self.phase = -1
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
        # Hunter can shoot anyone who's alive if he has a bullet even if he's dead
        if self.phase == 4 and self.player.role.id == 3 and self.player.role.bullet == 1 and votee.is_alive:
            return True
        # Normally you cannot vote on anyone if you are dead or the person you want to vote on is dead
        elif not (self.player.is_alive and votee.is_alive and not self.game_is_finished):
            return False
        # Witch at night to save werewolf votee
        elif self.phase == 3 and self.player.role.id == 2 and self.player.role.has_healing_potion and votee.id == self.werewolf_votee:
            return True
        elif votee.id == self.player.id:
            return False
        # Everyone during voting day
        elif self.phase == 0:
            return True
        # Werewolf at night
        elif self.phase == 1 and self.player.role.id == 1:
            return True
        # Seer at night
        elif self.phase == 2 and self.player.role.id == 4 and not self.seer_vote:
            return True
        # Witch at night to kill someone
        elif self.phase == 3 and self.player.role.id == 2 and self.player.role.has_killing_potion:
            return True
        return False

    def sees_role_of(self, player):
        if hasattr(player, 'role') and player.role is not None:
            if self.game_is_finished:
                role = Role.get_role_name_from_id(player.role.id).lower()
            # Werewolves see each other
            elif player.role.id == 1 and self.player.role.id == 1:
                role = Role.get_role_name_from_id(player.role.id).lower()
            # Everyone can see dead players
            elif not player.is_alive:
                role = Role.get_role_name_from_id(player.role.id).lower()
            # You can see your own role
            elif player.id == self.player.id:
                role = Role.get_role_name_from_id(player.role.id).lower()
            # Seer can see the role of selected person
            elif self.player.role.id == 4 and self.seer_vote and player.id == self.seer_vote:
                role = Role.get_role_name_from_id(player.role.id).lower()
            else:
                role = 'unknown'
        else:
            role = 'unknown'
        return role

    def vote_player(self, player_id):
        if self.phase == 0:
            vote = 'BASE_VOTE'
        elif self.phase == 1:
            vote = 'WEREWOLF_VOTE'
        elif self.phase == 2:
            self.handle_seer_vote(player_id)
            return
        elif self.phase == 3:
            self.handle_witch_vote(player_id)
            return
        elif self.phase == 4:
            vote = 'HUNTER_VOTE'
        message = {
            'action': vote,
            'sender_id': self.player.id,
            'selected_player_id': player_id
        }
        self.send_message(message)

    def handle_seer_vote(self, player_id):
        self.seer_vote = player_id
        player_frame = self.ui.get_player_frame_by_id(player_id)
        player_frame.add_role_image()
        self.ui.update_window()

    def handle_witch_vote(self, player_id):
        message = {
            'action': 'WITCH_VOTE',
        }
        key = 'save' if player_id == self.werewolf_votee else 'kill'
        message[key] = player_id
        self.send_message(message)

    def restart_game(self):
        self.send_message(
            {'action': 'NEW_GAME'}
        )

    def reset(self):
        self.game_is_finished = False
        self.round = 0
        self.phase = 0
        self.hunter_death_time = None
        self.werewolf_votee = -1
        self.seer_vote = None
        self.ui.reset_for_next_game()
