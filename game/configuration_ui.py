import customtkinter as ctk
import tkinter

ROOT_BACKGROUND = '#101010'


class ConfigurationUI(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(fg_color=ROOT_BACKGROUND)
        self.controller = controller

        self.geometry("320x320")
        self.title("Werewolves connector")
        self.minsize(250, 350)
        self.iconbitmap("resources/werewolves_icon.ico")
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # configure grid layout (3x3)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Label
        self.title_label = ctk.CTkLabel(self, text="Show deaths", font=ctk.CTkFont(size=21, weight="bold"))
        self.title_label.grid(row=0, column=1, pady=(25, 25), padx=(25, 25), sticky="s")

        # Name input
        check_var = tkinter.StringVar("on")

        self.checkbox = ctk.CTkCheckBox(master=self, text="On", variable=check_var, onvalue="on", offvalue="off")
