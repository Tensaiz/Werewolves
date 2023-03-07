import customtkinter as ctk
from tkinter import messagebox as msgb
import tkinter

ROOT_BACKGROUND = '#101010'
BUTTON_COLOR = '#4e0f11'
BUTTON_HOVER_COLOR = '#3E090B'


class AuthenticationUI(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(fg_color=ROOT_BACKGROUND)
        self.controller = controller
        self.connecting = False
        self.geometry("320x320")
        self.title("Werewolves connector")
        self.minsize(250, 350)
        self.iconbitmap("resources/werewolves_icon.ico")
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # configure grid layout (3x3)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Label
        self.title_label = ctk.CTkLabel(self, text="Log in", font=ctk.CTkFont(size=21, weight="bold"))
        self.title_label.grid(row=0, column=1, pady=(25, 25), padx=(25, 25), sticky="s")

        # # Name input
        # self.name = ctk.CTkEntry(self, placeholder_text="Name")
        # self.name.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="n")

        # # Server ip input
        # self.ip = ctk.CTkEntry(self, placeholder_text="IP Address")
        # self.ip.grid(row=1, column=1, pady=(25, 25), padx=(25, 25))

        # # Server port input
        # self.port = ctk.CTkEntry(self, placeholder_text="Port")
        # self.port.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="s")
        # Name input
        self.name = ctk.CTkEntry(self, placeholder_text="Name")
        self.name.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="n")
        self.name.insert(tkinter.END, "a")

        # Server ip input
        self.ip = ctk.CTkEntry(self, placeholder_text="IP Address")
        self.ip.grid(row=1, column=1, pady=(25, 25), padx=(25, 25))
        self.ip.insert(tkinter.END, "localhost")

        # Server port input
        self.port = ctk.CTkEntry(self, placeholder_text="Port")
        self.port.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="s")
        self.port.insert(tkinter.END, "27015")

        # Connect button
        self.connect_button = ctk.CTkButton(self, text="Connect", font=ctk.CTkFont(size=12, weight="bold"), fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=self.connect)
        self.connect_button.grid(row=2, column=1, padx=(25, 25), pady=(10, 50), sticky="s")

    def connect(self):
        if self.connecting:
            return

        name = self.name.get()
        ip = self.ip.get()
        port = self.port.get()

        if len(name) > 0 and len(ip) > 0 and len(port) > 0:
            print(name, ip, port)
            try:
                self.connect_button["state"] = tkinter.DISABLED
                self.connecting = True
                self.controller.connect(name, ip, port)
            except Exception as e:
                print(e)
                msgb.askokcancel("Connection", f"Connection to {ip}:{port} failed!")
                self.connect_button["state"] = tkinter.NORMAL
                self.connecting = False
