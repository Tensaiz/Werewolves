import customtkinter as ctk
import tkinter
from tkinter import messagebox as msgb

ROOT_BACKGROUND = '#101010'
BUTTON_COLOR = '#4e0f11'
BUTTON_HOVER_COLOR = '#3E090B'

CHECKBOX_SETTINGS = ["hide_deaths", "seer_role", "witch_role", "hunter_role", "innocent_role", "cupid_role"]
TIME_SETTINGS = {
    "discussion_time": "base_round_time",
    "werewolf_time": "werewolf_round_time",
    "transition_time": "transition_time",
    "role_time": "role_decide_time"
}


class ConfigurationUI(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(fg_color=ROOT_BACKGROUND)
        self.controller = controller

        self.geometry("350x550")
        self.title("Configuration")
        self.minsize(340, 600)
        self.iconbitmap("resources/werewolves_icon.ico")

        total_rows = len(CHECKBOX_SETTINGS) + len(TIME_SETTINGS) + 2
        self.grid_rowconfigure(tuple(range(total_rows)), weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.title_label = ctk.CTkLabel(self, text="Game settings", font=ctk.CTkFont(size=21, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(25, 25), padx=(25, 25), sticky="w", columnspan=2)

        for i, setting in enumerate(TIME_SETTINGS.keys()):
            var_name = f"{setting}_var"
            setting_name = setting.replace("_", " ").capitalize()
            setattr(self, var_name, tkinter.StringVar(self, value=f"{self.controller.config.get(TIME_SETTINGS[setting])}"))
            label = ctk.CTkLabel(self, text=(setting_name + " (s)"))
            label.grid(row=1 + i, column=0, pady=(5, 5), padx=(25, 25), sticky="w")
            entry = ctk.CTkEntry(self, textvariable=getattr(self, var_name), placeholder_text=setting_name)
            entry.grid(row=1 + i, column=1, pady=(5, 5), padx=(25, 25))
            setattr(self, f"{setting}_entry", entry)

        from_row = len(CHECKBOX_SETTINGS) - 1
        for i, setting in enumerate(CHECKBOX_SETTINGS):
            var_name = f"{setting}_var"
            setting_name = setting.replace("_", " ").capitalize()
            setattr(self, var_name, tkinter.BooleanVar(self, value=self.controller.config.get(setting)))  # tkinter.StringVar(self, value="on"))
            checkbox = ctk.CTkCheckBox(self, variable=getattr(self, var_name), text=setting_name, onvalue=True, offvalue=False, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR)
            checkbox.grid(row=from_row + i, column=0, pady=(5, 5), padx=(25, 25), sticky="w", columnspan=2)
            setattr(self, f"{setting}_checkbox", checkbox)

        self.finish_button = ctk.CTkButton(self, text="Save", font=ctk.CTkFont(size=12, weight="bold"), fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=self.save_configuration)
        self.finish_button.grid(row=total_rows-1, column=0, padx=(10, 10), pady=(10, 10), sticky="ew", columnspan=2)

    def save_configuration(self):
        did_crash = False
        for setting in TIME_SETTINGS:
            var_name = f"{setting}_var"
            try:
                var_value = int(getattr(self, var_name).get())
                self.controller.config.set(TIME_SETTINGS[setting], var_value)
            except Exception:
                did_crash = True
                pname = setting.replace("_", " ")
                msgb.askokcancel("Configuration", f"Invalid value for {pname}")

        for setting in CHECKBOX_SETTINGS:
            var_name = f"{setting}_var"
            var_value = getattr(self, var_name).get()
            self.controller.config.set(setting, var_value)

        self.controller.update_config()

        if not did_crash:
            self.destroy()
