import tkinter
import customtkinter as ctk
import time
from typing import List

from player import Player


class PlayerList(ctk.CTkFrame):
    def __init__(self, master, players: List[Player], **kwargs):
        super().__init__(master, **kwargs)

        for i, player in enumerate(players):
            label = ctk.CTkLabel(self, text=player.name)
            label.grid(row=i, column=0, padx=20, pady=10)
            button = ctk.CTkButton(self, text="Vote", command=lambda p=player: self.vote_player(p), width=50)
            button.grid(row=i, column=2, padx=20)

    def vote_player(self, player: Player):
        print(f"Voted for {player.name}")


class BaseGame():
    def __init__(self, discussion_time) -> None:
        self.discussion_time = discussion_time
        self.players: List[Player] = []

    def set_players(self, players):
        self.players = players

    def voting(self):
        voting_window = ctk.CTk()
        voting_window.geometry("240x400")
        voting_window.title("Stemmen")
        label = ctk.CTkLabel(voting_window, text="Stem op een van de deelnemers")
        label.pack(side="top", fill="x", pady=10)

        players = PlayerList(voting_window, self.players)
        players.place(relx=.5, rely=.5, anchor=tkinter.CENTER)

        ok_button = ctk.CTkButton(voting_window, text="Okay", command=voting_window.destroy)
        ok_button.place(relx=0.5, rely=0.9, anchor=tkinter.CENTER)
        voting_window.mainloop()

    def start(self):
        # t = Timer(self.discussion_time, self.voting)
        # t.start()
        time.sleep(self.discussion_time)
        # Voting happens
        self.voting()
        # Check game conditions

        # Go to night
        # - Werewolves wakeup, everyone gets muted except for them

        # Wake up again
        # Announce dead people
        # Repeat


bg = BaseGame(1)
players = [Player("Matuno"), Player("Matdos"), Player("Mattrias"), Player("Matquattros"), Player("Matpentos")]
bg.set_players(players)
bg.start()
