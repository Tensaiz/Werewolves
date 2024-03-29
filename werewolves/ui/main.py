import tkinter
from PIL import Image
import customtkinter as ctk
from werewolves.game.role import Role
import werewolves.game.controller as cc
from werewolves.ui.config import ConfigurationUI

ROOT_BACKGROUND = '#101010'
SCROLLABLE_FRAME_COLOR = '#222020'
PLAYER_FRAME_COLOR = '#191716'
PLAYER_SELECTED_FRAME_COLOR = '#7E8D85'
TEAM_WON_COLOR = '#09814A'
TEAM_LOST_COLOR = '#4e0f11'
BUTTON_COLOR = '#4e0f11'
BUTTON_HOVER_COLOR = '#3E090B'


class MainUI(ctk.CTk):
    def __init__(self, controller):
        super().__init__(fg_color=ROOT_BACKGROUND)
        self.controller = controller
        self.player_frame_list = []
        self.pregame_widgets = []
        self.geometry("420x620")
        self.title("Weerwolven")
        self.minsize(400, 500)
        self.maxsize(500, 700)

        # Images
        self.is_pregame_lobby = True
        self.is_daytime = True

        self.default_font_bold = ctk.CTkFont(size=14, weight="bold")
        self.default_font_button = ctk.CTkFont(size=12, weight="bold")

        icon = tkinter.PhotoImage(file="resources/werewolves_icon.png")
        self.iconphoto(False, icon)

        self.init_pregame_vars()
        self.write_init_UI()

    def init_pregame_vars(self):
        self.restart_button = None
        self.player_list_frame = None
        self.current_vote_id = None
        self.pregame_label = None
        self.player_count = None
        self.player_required_count = None
        self.start_game_button = None
        self.mute_button = None
        self.role_label = None
        self.daytime_label = None
        self.timer_label = None
        self.deafened_label = None
        self.state_label = None
        self.role_image = None
        self.config_button = None

    def write_init_UI(self):
        # configure grid layout (3x3)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="a")
        self.grid_columnconfigure(1, weight=1, uniform="a")
        self.grid_columnconfigure(2, weight=1, uniform="a")

        self.draw_top()

        # Player list
        self.player_list_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=SCROLLABLE_FRAME_COLOR)
        self.player_list_frame.grid(row=2, column=0, columnspan=3, padx=(25, 25), sticky="nsew")
        self.player_list_frame.columnconfigure(0, weight=1)

        # Player objects
        self.update_players_list()

        self.draw_bottom()

    def update_timer(self, t):
        self.timer_label.configure(text=t)

        if t > 0 and not self.controller.game_is_finished:
            self.after(1000, lambda: self.update_timer(t - 1))

    def update_window(self):
        self.draw_top()
        self.update_players_list()
        self.draw_bottom()
        self.update()

    def draw_top(self):
        if not self.is_pregame_lobby and self.controller.player.role is not None:
            if self.role_label is None:
                self.role_label = ctk.CTkLabel(self, text=f"{Role.get_role_name_from_id(self.controller.player.role.id)}", font=self.default_font_bold)
                self.role_label.grid(row=0, column=0, pady=10, padx=(25, 0), sticky="nws")
            self.role_label.configure(text=f"{Role.get_role_name_from_id(self.controller.player.role.id)}")

            day_state = self.controller.get_phase_name(self.controller.phase)

            if self.daytime_label is None:
                self.daytime_label = ctk.CTkLabel(self, text=day_state, font=self.default_font_bold)
                self.daytime_label.grid(row=0, column=1, pady=10, sticky="news")
            self.daytime_label.configure(text=day_state)

            if self.timer_label is None:
                # Timer
                self.timer_label = ctk.CTkLabel(self, text="", font=self.default_font_bold)
                self.timer_label.grid(row=0, column=2, padx=(0, 25), pady=10, sticky="nes")
        else:
            # Pre game lobby label
            if self.pregame_label is None:
                self.pregame_label = ctk.CTkLabel(self, text="Pre-game Lobby - Start game when everyone is in", font=self.default_font_bold)
                self.pregame_label.grid(row=0, column=0, columnspan=3, pady=10, padx=(25, 25), sticky="ew")

            # Player count
            if self.player_count is None:
                self.player_count = ctk.CTkLabel(self, text=f"Players: {len(self.controller.players)}", font=self.default_font_bold)
                self.player_count.grid(row=1, column=0, columnspan=3, pady=(0, 0), padx=(25, 25), sticky="enw")
            self.player_count.configure(text=f"Players: {len(self.controller.players)}")

            # Player required count
            players_required = cc.MIN_PLAYERS - len(self.controller.players)
            players_required_text = players_required if players_required >= 0 else 0
            if self.player_required_count is None:
                self.player_required_count = ctk.CTkLabel(self, text=f"{players_required_text} more players required", font=self.default_font_bold)
                self.player_required_count.grid(row=1, column=0, columnspan=3, pady=(25, 0), padx=(25, 25), sticky="new")
            self.player_required_count.configure(text=f"{players_required_text} more players required")

    def draw_bottom(self):
        if self.mute_button is None:
            # Mute button
            self.mute_button = ctk.CTkButton(self, width=100, text="Mute", font=self.default_font_button, command=self.toggle_mute, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
            self.mute_button.grid(row=3, column=0, padx=(25, 0), pady=(10, 10), sticky="ew")

        if self.deafened_label is None:
            # Deafened icon
            self.deafened_label = ctk.CTkLabel(self, text='Not deafened', font=self.default_font_button)

        deafened_col = 1 if not self.is_pregame_lobby or (self.is_pregame_lobby and self.controller.is_player_host) else 2
        self.deafened_label.grid(row=3, column=deafened_col, pady=(10, 10), sticky="ew")

        if self.is_pregame_lobby and self.controller.is_player_host and self.config_button is None:
            # Gear icon
            self.config_button = ctk.CTkButton(self, width=100, text="Config", font=self.default_font_button, command=self.configure_game, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
            self.config_button.grid(row=3, column=2, padx=(0, 25), pady=(10, 10), sticky="ew")

        if not self.is_pregame_lobby:
            if self.config_button is not None:
                self.config_button.grid_remove()
            if self.state_label is None:
                # Living state text
                self.state_label = ctk.CTkLabel(self, text="Alive", font=self.default_font_button)
                self.state_label.grid(row=3, column=2, padx=(0, 25), pady=(10, 10), sticky="ew")
        else:
            if not self.controller.is_player_host:
                return

            state = tkinter.NORMAL if cc.MIN_PLAYERS - len(self.controller.players) <= 0 else tkinter.DISABLED
            if self.start_game_button is None:
                self.start_game_button = ctk.CTkButton(self, state=state, width=100, text="Start game",
                                                       font=self.default_font_button, command=self.start_game, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
                self.start_game_button.grid(row=4, column=1, padx=(10, 10), pady=10, sticky="ew")

            self.start_game_button.configure(state=state)

    def update_players_list(self):
        current_players = list(map(lambda pn: pn.player, self.player_frame_list))
        for i, player in enumerate(self.controller.players):
            if i < len(current_players):
                if current_players[i].id != player.id:
                    # other player
                    self.player_frame_list[i].after(200, self.player_frame_list[i].destroy)
                    self.player_frame_list[i] = PlayerName(self.player_list_frame, player, self.controller, self.is_pregame_lobby, self.vote_player, fg_color=PLAYER_FRAME_COLOR)
                    self.player_frame_list[i].grid(row=i, column=0, padx=(10, 10), pady=10, sticky="we")

                else:
                    # Update player
                    self.player_frame_list[i].player = player

                    if not self.is_pregame_lobby:
                        # Mark player as dead
                        if not player.is_alive:
                            self.player_frame_list[i].mark_dead()
                        # Add vote button on players that are votable
                        self.show_or_hide_vote_button(self.player_frame_list[i])
                        # Add role image
                        self.player_frame_list[i].add_role_image()
            else:
                self.player_frame_list.append(PlayerName(self.player_list_frame, player, self.controller, self.is_pregame_lobby, self.vote_player, fg_color=PLAYER_FRAME_COLOR))
                self.player_frame_list[-1].grid(row=i, column=0, padx=(10, 10), pady=10, sticky="we")

        if len(current_players) > len(self.controller.players):
            for i in range(len(self.controller.players), len(current_players)):
                self.player_frame_list[i].destroy()
                del self.player_frame_list[i]

    def show_or_hide_vote_button(self, player_frame):
        can_vote = self.controller.can_vote_on(player_frame.player)
        if can_vote:
            player_frame.add_vote_button(self.vote_player)
        else:
            if player_frame.vote:
                player_frame.hide_vote_button()

    def update_day_state(self, is_day):
        self.is_daytime = is_day
        text = "The sun has risen" if self.is_daytime else "Night has come"
        self.role_label.configure(text=text)

    def update_living(self, is_alive):
        text = "Alive" if is_alive else "Dead"
        self.state_label.configure(text=text)
        if not is_alive:
            self.update_muted(True)

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
        self.remove_previous_mark(player_id)
        self.mark_voted(player_id)
        self.current_vote_id = player_id

    def remove_previous_mark(self, player_id):
        if self.controller.phase == 3 and self.current_vote_id == self.controller.werewolf_votee:
            return
        elif self.current_vote_id:
            self.remove_previous_marks(self.current_vote_id)

    def mark_voted(self, player_id):
        for player_frame in self.player_frame_list:
            if player_frame.player.id == player_id:
                player_frame.configure(fg_color=PLAYER_SELECTED_FRAME_COLOR)

    def remove_previous_marks(self, previous_votee):
        for player_frame in self.player_frame_list:
            if player_frame.player.id == previous_votee:
                player_frame.configure(fg_color=PLAYER_FRAME_COLOR)

    def remove_voting_marks(self):
        for player_frame in self.player_frame_list:
            player_frame.configure(fg_color=PLAYER_FRAME_COLOR)

    def show_final_game_ui(self, winning_team):
        for player_frame in self.player_frame_list:
            if player_frame.player.role.id == winning_team:
                player_frame.configure(fg_color=TEAM_WON_COLOR)
            else:
                player_frame.configure(fg_color=TEAM_LOST_COLOR)
            if player_frame.vote:
                player_frame.hide_vote_button()
        self.show_restart_button()

    def configure_game(self):
        self.config_ui = ConfigurationUI(self.controller)
        self.config_ui.attributes('-topmost', True)

    def reset_for_next_game(self):
        for player_frame in self.player_frame_list:
            player_frame.configure(fg_color=PLAYER_FRAME_COLOR, border_width=0, border_color=PLAYER_FRAME_COLOR)
            if player_frame.dead_image:
                player_frame.dead_image.grid_forget()
        if self.restart_button:
            self.restart_button.destroy()
        self.current_vote_id = None

    def show_restart_button(self):
        if not self.controller.is_player_host:
            return

        self.restart_button = ctk.CTkButton(self, width=75, text="Restart game", font=self.default_font_button,
                                            command=self.controller.restart_game, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
        self.restart_button.grid(row=4, column=1, padx=(10, 10), pady=(10, 20), sticky="ew")

    def toggle_mute(self):
        self.controller.network_client.toggle_mute()
        text = "Unmute" if self.controller.network_client.is_muted else "Mute"
        self.mute_button.configure(text=text)

    def start_game(self):
        self.controller.start_game()

    def show_witch_ui(self):
        if self.controller.player.role.id != 2:
            return
        for player_frame in self.player_frame_list:
            # Mark werewolf votee for witch
            if player_frame.player.id == self.controller.werewolf_votee and self.controller.player.role.has_healing_potion:
                player_frame.configure(border_width=2, border_color='red')
                player_frame.vote.configure(text="Save")
            elif player_frame.player.is_alive and player_frame.vote:
                player_frame.vote.configure(text="Kill")

    def remove_witch_ui(self):
        if self.controller.player.role.id != 2:
            return
        for player_frame in self.player_frame_list:
            # Mark werewolf votee for witch
            if player_frame.player.id == self.controller.werewolf_votee:
                player_frame.configure(border_width=0, border_color=PLAYER_FRAME_COLOR)
                player_frame.vote.configure(text="Vote")

    def purge_pregame_widgets(self):
        self.pregame_label.grid_remove()
        self.player_count.grid_remove()
        self.player_required_count.grid_remove()
        if self.start_game_button:
            self.start_game_button.grid_remove()

    def mark_player_speaking(self, playerid):
        player_frame = self.get_player_frame_by_id(playerid)
        player_frame.configure(border_width=2, border_color='green')

    def mark_player_done_speaking(self, playerid):
        player_frame = self.get_player_frame_by_id(playerid)
        player_frame.configure(border_width=0, border_color=PLAYER_FRAME_COLOR)

    def get_player_frame_by_id(self, playerid):
        for player_frame in self.player_frame_list:
            if player_frame.player.id == playerid:
                return player_frame


class PlayerName(ctk.CTkFrame):
    def __init__(self, master, player, controller, is_pregame_lobby, vote_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.player = player
        self.controller = controller
        self.player_name = player.name
        self.vote = None
        self.role_image = None
        self.height = 100
        self.dead_image = None
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.default_font_bold = ctk.CTkFont(size=14, weight="bold")
        self.default_font_button = ctk.CTkFont(size=12, weight="bold")

        player_id = player.id

        self.label = ctk.CTkLabel(self, text=self.player.name, font=self.default_font_bold, anchor="w")
        self.label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        if not is_pregame_lobby:
            if self.controller.can_vote_on(player):
                self.vote = ctk.CTkButton(self, width=50, text="Vote", font=self.default_font_button,
                                          command=lambda p=player_id: vote_callback(p), fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
                self.vote.grid(row=0, column=2, columnspan=2, padx=(0, 10), pady=10, sticky="e")

        image = ctk.CTkImage(dark_image=Image.open('./resources/dead.png'),
                             size=(30, 30))
        self.dead_image = ctk.CTkButton(self, image=image, text='', state='disabled', width=30, fg_color='transparent')
        self.dead_image.grid(row=0, column=2, sticky="e")
        self.dead_image.grid_forget()

    def add_role_image(self):
        role = self.controller.sees_role_of(self.player)
        image = ctk.CTkImage(dark_image=Image.open(f"./resources/{role}.png"),
                             size=(30, 30))
        if self.role_image is None:
            self.role_image = ctk.CTkButton(self, image=image, text='', state='disabled', width=30, fg_color='transparent')
            self.role_image.grid(row=0, column=0, sticky="w")
        else:
            self.role_image.configure(image=image)

    def add_vote_button(self, vote_callback):
        self.vote = ctk.CTkButton(self, width=50, text="Vote", font=self.default_font_button,
                                  command=lambda p=self.player.id: vote_callback(p), fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
        self.vote.grid(row=0, column=1, columnspan=2, padx=(0, 10), pady=10, sticky="e")

    def hide_vote_button(self):
        self.vote.grid_forget()

    def mark_dead(self):
        if not self.controller.config.hide_deaths:
            self.dead_image.grid(row=0, column=2, sticky="e")
