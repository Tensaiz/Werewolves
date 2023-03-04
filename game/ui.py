import tkinter
import customtkinter as ctk
import datetime


class UI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.player_frame_list = []
        self.geometry("420x620")
        self.title("Weerwolven")
        self.minsize(300, 200)

        self.is_daytime = True

        # configure grid layout (3x3)
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Day / night text top left
        self.daytime_label = ctk.CTkLabel(self, text="Villager", font=ctk.CTkFont(size=21, weight="bold"))
        self.daytime_label.grid(row=0, column=0, pady=(25, 25), padx=(25, 25), sticky="w")

        # Timer
        self.timer_label = ctk.CTkLabel(self, text="0.0", font=ctk.CTkFont(size=21, weight="bold"))
        self.timer_label.grid(row=0, column=2, padx=(0, 25), pady=(10, 0), sticky="e")
        self.update_timer()


        # Mute button
        self.mute_button = ctk.CTkButton(self, width=100, text="Mute", font=ctk.CTkFont(size=12, weight="bold"), command=self.toggle_mute)
        self.mute_button.grid(row=2, column=0, padx=(25, 25), pady=(10, 10), sticky="w")

        # Deafened icon
        self.deafened_label = ctk.CTkLabel(self, text='Not deafened', font=ctk.CTkFont(size=12, weight="bold"))
        self.deafened_label.grid(row=2, column=1, padx=(0, 50), pady=(10, 10), sticky="w")

        # Living state text
        self.state_label = ctk.CTkLabel(self, text="Alive", font=ctk.CTkFont(size=12, weight="bold"))
        self.state_label.grid(row=2, column=2, padx=(0, 25), pady=(10, 10), sticky="nsew")

        # Player list
        self.player_list_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.player_list_frame.grid(row=1, column=0, columnspan=3, padx=(25, 25), sticky="nsew")
        self.player_list_frame.grid_rowconfigure(1, weight=1)

        # Player objects
        for i, player in enumerate(self.controller.players):
            self.player_frame_list.append(PlayerName(self.player_list_frame, player, self.vote_player))
            self.player_frame_list[-1].grid(row=i, column=0, padx=(20, 10), pady=10, sticky="nsew")

    def update_timer(self, t=None):
        t = 60 - datetime.datetime.now().second
        self.timer_label.configure(text=t)
        self.after(1000, self.update_timer)

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


class PlayerName(ctk.CTkFrame):
    def __init__(self, master, player, vote_callback):
        super().__init__(master)
        self.player = player
        self.name = player.name
        self.height = 100

        player_id = player.id

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text=str(self.name), font=ctk.CTkFont(size=12, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.vote = ctk.CTkButton(self, width=50, text="Vote", font=ctk.CTkFont(size=12, weight="bold"), command=lambda p=player_id: vote_callback(p))
        self.vote.grid(row=0, column=1, padx=(0, 10), pady=10)
