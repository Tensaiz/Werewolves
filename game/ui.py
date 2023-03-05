import tkinter
import customtkinter as ctk
import datetime

from game.role import Role


class UI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.player_frame_list = []
        self.geometry("420x620")
        self.title("Weerwolven")
        self.minsize(400, 200)

        self.is_pregame_lobby = True
        self.is_daytime = True

        # configure grid layout (3x3)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.draw_top()

        # Player list
        self.player_list_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.player_list_frame.grid(row=2, column=0, columnspan=3, padx=(25, 25), sticky="nsew")
        self.player_list_frame.grid_rowconfigure(1, weight=1)

        # Player objects
        self.update_players_list()

        self.draw_bottom()

    def update_timer(self, t=None):
        t = 60 - datetime.datetime.now().second
        self.timer_label.configure(text=t)
        self.after(1000, self.update_timer)

    def update_window(self):
        self.draw_top()
        self.update_players_list()
        self.draw_bottom()

    def draw_top(self):
        if not self.is_pregame_lobby and self.controller.player.role is not None:
            # Day / night text top left
            self.daytime_label = ctk.CTkLabel(self, text=f"{Role.get_role_name_from_id(self.controller.player.role)}", font=ctk.CTkFont(size=21, weight="bold"))
            self.daytime_label.grid(row=0, column=0, pady=(10, 10), padx=(25, 25), sticky="w")

            # Timer
            self.timer_label = ctk.CTkLabel(self, text="0.0", font=ctk.CTkFont(size=21, weight="bold"))
            self.timer_label.grid(row=0, column=2, padx=(0, 25), pady=(10, 10), sticky="e")
            self.update_timer()
        else:
            # Pre game lobby label
            self.pregame_label = ctk.CTkLabel(self, text="Pre-game Lobby - Start game when everyone is in", font=ctk.CTkFont(size=12, weight="bold"))
            self.pregame_label.grid(row=0, column=0, columnspan=3, pady=(25, 0), padx=(25, 25))

            # Player count
            self.player_count = ctk.CTkLabel(self, text=f"Players: {len(self.controller.players)}", font=ctk.CTkFont(size=12, weight="bold"))
            self.player_count.grid(row=1, column=0, columnspan=2, pady=(0, 0), padx=(25, 25), sticky="n")

            # Player required count
            players_required = self.controller.MIN_PLAYERS - len(self.controller.players) 
            players_required_text = players_required if players_required >= 0 else 0
            self.player_required_count = ctk.CTkLabel(self, text=f"{players_required_text} more players required", font=ctk.CTkFont(size=12, weight="bold"))
            self.player_required_count.grid(row=1, column=0, columnspan=2, pady=(25, 0), padx=(25, 25), sticky="s")

    def draw_bottom(self):
        # Mute button
        self.mute_button = ctk.CTkButton(self, width=100, text="Mute", font=ctk.CTkFont(size=12, weight="bold"), command=self.toggle_mute)
        self.mute_button.grid(row=3, column=0, padx=(25, 25), pady=(10, 10), sticky="w")

        # Deafened icon
        self.deafened_label = ctk.CTkLabel(self, text='Not deafened', font=ctk.CTkFont(size=12, weight="bold"))
        self.deafened_label.grid(row=3, column=1, padx=(10, 50), pady=(10, 10), sticky="w")

        if not self.is_pregame_lobby:
            # Living state text
            self.state_label = ctk.CTkLabel(self, text="Alive", font=ctk.CTkFont(size=12, weight="bold"))
            self.state_label.grid(row=3, column=2, padx=(0, 25), pady=(10, 10), sticky="nsew")
        else:
            state = tkinter.NORMAL if self.controller.MIN_PLAYERS - len(self.controller.players) <= 0 else tkinter.DISABLED
            self.start_game_button = ctk.CTkButton(self, state=state, width=100, text="Start game", font=ctk.CTkFont(size=12, weight="bold"), command=self.start_game)
            self.start_game_button.grid(row=4, column=1, padx=(10, 10), pady=10, sticky="w")

    def update_players_list(self):
        for frame in self.player_frame_list:
            frame.destroy()
        self.player_frame_list = []

        for i, player in enumerate(self.controller.players):
            self.player_frame_list.append(PlayerName(self.player_list_frame, player, self.controller, self.is_pregame_lobby, self.vote_player))
            self.player_frame_list[-1].grid(row=i, column=0, padx=(20, 10), pady=10, sticky="nsew")

    def update_day_state(self, state):
        self.is_daytime = state
        text = "The sun has risen" if self.is_daytime else "Night has come"
        self.daytime_label.configure(text=text)

    def update_living(self, is_alive):
        text = "Alive" if self.controller.player.is_alive else "X_X"
        self.state_label.configure(text=text)

    def update_muted(self, is_muted):
        if is_muted:
            text = 'Unmute'
            state = tkinter.DISABLED
        else:
            text = 'Mute'
            state = tkinter.NORMAL

        self.mute_button.configure(text=text, state=state)

    def update_deafened(self, is_deafened):
        text = 'Deafened' if is_deafened else 'Not deafened'
        self.deafened_label.configure(text=text)

    def vote_player(self, player_id):
        self.controller.vote_player(player_id)

    def werewolves_win(self):
        for player_frame in self.player_frame_list:
            if player_frame.player.role == 1:
                player_frame.bg_color = 'green'
            else:
                player_frame.bg_color = 'red'

    def villagers_win(self):
        for player_frame in self.player_frame_list:
            if player_frame.player.role == 0:
                player_frame.bg_color = 'green'
            else:
                player_frame.bg_color = 'red'

    def toggle_mute(self):
        self.controller.network_client.toggle_mute()
        text = "Unmute" if self.controller.network_client.is_muted else "Mute"
        self.mute_button.configure(text=text)

    def start_game(self):
        self.controller.start_game()

    def purge_pregame_widgets(self):
        self.pregame_label.destroy()
        self.player_count.destroy()
        self.player_required_count.destroy()
        self.start_game_button.destroy()


class PlayerName(ctk.CTkFrame):
    def __init__(self, master, player, controller, is_pregame_lobby, vote_callback):
        super().__init__(master)
        self.player = player
        self.controller = controller
        self.player_name = player.name
        self.height = 100

        player_id = player.id

        self.grid_columnconfigure(0, weight=1)

        textcolor = 'red' if self.controller.player.role == 1 and player.role == 1 else None

        self.label = ctk.CTkLabel(self, text=str(self.player_name), text_color=textcolor, font=ctk.CTkFont(size=12, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        if not is_pregame_lobby:
            self.vote = ctk.CTkButton(self, width=50, text="Vote", font=ctk.CTkFont(size=12, weight="bold"), command=lambda p=player_id: vote_callback(p))
            self.vote.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
