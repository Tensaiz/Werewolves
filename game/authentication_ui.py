import customtkinter as ctk
import tkinter


class AuthenticationUI(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.geometry("320x320")
        self.title("Werewolves connector")
        self.minsize(250, 350)

        self.protocol("WM_DELETE_WINDOW", self.quit)

        # configure grid layout (3x3)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Label
        self.title_label = ctk.CTkLabel(self, text="Log in", font=ctk.CTkFont(size=21, weight="bold"))
        self.title_label.grid(row=0, column=1, pady=(25, 25), padx=(25, 25), sticky="s")

        # Name input
        self.name = ctk.CTkEntry(self, placeholder_text="Name")
        self.name.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="n")

        # Server ip input
        self.ip = ctk.CTkEntry(self, placeholder_text="IP Address")
        self.ip.grid(row=1, column=1, pady=(25, 25), padx=(25, 25))

        # Server port input
        self.port = ctk.CTkEntry(self, placeholder_text="Port")
        self.port.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="s")
        # Name input
        # self.name = ctk.CTkEntry(self, placeholder_text="Name")
        # self.name.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="n")
        # self.name.insert(tkinter.END, "a")

        # # Server ip input
        # self.ip = ctk.CTkEntry(self, placeholder_text="IP Address")
        # self.ip.grid(row=1, column=1, pady=(25, 25), padx=(25, 25))
        # self.ip.insert(tkinter.END, "localhost")

        # # Server port input
        # self.port = ctk.CTkEntry(self, placeholder_text="Port")
        # self.port.grid(row=1, column=1, pady=(0, 0), padx=(25, 25), sticky="s")
        # self.port.insert(tkinter.END, "27015")

        # Connect button
        self.connect_button = ctk.CTkButton(self, text="Connect", font=ctk.CTkFont(size=12, weight="bold"), command=self.connect)
        self.connect_button.grid(row=2, column=1, padx=(25, 25), pady=(10, 50), sticky="s")

    def connect(self):
        name = self.name.get()
        ip = self.ip.get()
        port = self.port.get()

        if len(name) > 0 and len(ip) > 0 and len(port) > 0:
            print(name, ip, port)
            self.controller.connect(name, ip, port)
