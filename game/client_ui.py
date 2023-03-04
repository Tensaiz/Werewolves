import tkinter
import tkinter.messagebox
import customtkinter as ctk


class WerewolfClientUI():
    def __init__(self):
        self.client = None
        self.players = [0, 1, 2, 3, 4, 5]
        self.app = UI(self)


    def set_client(self, client):
        self.client = client

    def connect(self):
        pass

    def disconnect(self):
        pass

    def send_message(self):
        message = self.input_entry.get()
        self.input_entry.delete(0, 'end')
        self.client.send_text(message)


class UI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.player_frame_list = []
        self.geometry("1280x720")
        self.title("Weerwolven")
        self.minsize(300, 200)

        # configure grid layout (3x3)
        self.grid_rowconfigure((1, 2), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Day / night text top left
        self.daytime_label = ctk.CTkLabel(self, text="The sun has risen", font=ctk.CTkFont(size=20, weight="bold"))
        self.daytime_label.grid(row=0, column=0, pady=(20, 20), padx=(20))



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


    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def button_callback(self):
        self.textbox.insert("insert", self.combobox.get() + "\n")


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