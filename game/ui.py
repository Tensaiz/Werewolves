import customtkinter as ctk
import datetime


class UI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.player_frame_list = []
        self.geometry("920x480")
        self.title("Weerwolven")
        self.minsize(300, 200)

        self.is_daytime = True

        # configure grid layout (3x3)
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Day / night text top left
        self.daytime_label = ctk.CTkLabel(self, text="The sun has risen", font=ctk.CTkFont(size=20, weight="bold"))
        self.daytime_label.grid(row=0, column=0, pady=(20, 20), padx=(20))

        # Mute button
        self.vote = ctk.CTkButton(self, width=100, text="Mute", font=ctk.CTkFont(size=12, weight="bold"))
        self.vote.grid(row=2, column=0, padx=(10, 10), pady=(10, 10))

        # Role text
        self.role_label = ctk.CTkLabel(self, text="Role", font=ctk.CTkFont(size=42, weight="bold"))
        self.role_label.grid(row=1, column=1, padx=(0, 150), pady=(0, 75), sticky="nsew")

        # Timer
        self.timer_label = ctk.CTkLabel(self, text="0.0", font=ctk.CTkFont(size=42, weight="bold"))
        self.timer_label.grid(row=0, column=1, padx=(0, 25), pady=(10, 0), sticky="e")
        self.update_timer()

        # Living state text
        self.state_label = ctk.CTkLabel(self, text="Still alive", font=ctk.CTkFont(size=28, weight="bold"))
        self.state_label.grid(row=2, column=1, padx=(0, 25), pady=(0, 10), sticky="e")

        # Right side frame with players and statuses
        self.sidebar_frame = ctk.CTkFrame(self, width=500, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Players", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.client_list = ctk.CTkScrollableFrame(self.sidebar_frame, width=250)
        self.client_list.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.client_list.grid_columnconfigure(0, weight=1)

        # Player objects
        for i, player in enumerate(self.controller.players):
            self.player_frame_list.append(PlayerName(self.client_list, player))
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
        text = "Still alive" if self.controller.player.is_alive else "X_X"
        self.state_label.configure(text=text)

    def update_muted(self, is_muted):
        pass

    def update_deafened(self, is_deafened):
        pass


class PlayerName(ctk.CTkFrame):
    def __init__(self, master, name):
        super().__init__(master)
        self.name = name
        self.height = 100

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text=str(self.name), font=ctk.CTkFont(size=12, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.vote = ctk.CTkButton(self, width=50, text="Vote", font=ctk.CTkFont(size=12, weight="bold"))
        self.vote.grid(row=0, column=1, padx=(0, 10), pady=10)