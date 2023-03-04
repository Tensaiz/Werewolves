import customtkinter as ctk
import time


class BaseGame():
    def __init__(self, discussion_time) -> None:
        self.discussion_time = discussion_time

    def voting(self):
        voting_window = ctk.CTk()
        voting_window.title("Stemmen")
        label = ctk.Label(voting_window, text="Stem op een van de deelnemers")
        label.pack(side="top", fill="x", pady=10)

        B1 = ctk.Button(voting_window, text="Okay", command=voting_window.destroy)
        B1.pack()
        voting_window.mainloop()

    def start(self):
        # t = Timer(self.discussion_time, self.voting)
        # t.start()
        time.sleep(self.discussion_time)
        # Voting happens

        # Check game conditions

        # Go to night
        # - Werewolves wakeup, everyone gets muted except for them

        # Wake up again
        # Announce dead people
        # Repeat


bg = BaseGame(1)
bg.start()
