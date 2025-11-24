import os
import shutil
import subprocess
import customtkinter as ctk
from main.config import load_config
from main._template import LOGGER

CONFIG = load_config("main/config.json")


class UnrealToolsUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.paths = CONFIG.get("paths", {})

        # Title
        title = ctk.CTkLabel(self, text="Unreal Tools", font=("Segoe UI", 22))
        title.grid(row=0, column=0, columnspan=3, pady=(10, 15))

        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=0)  # Button Spalte

        # -------------------------
        # TEMP FOLDERS SECTION
        # -------------------------
        self.temp_label = ctk.CTkLabel(btn_frame, text="Delete Temporary Folders")
        self.temp_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        self.temp_folders = self._get_temp_folders()
        self.temp_buttons = {}

        for i, (name, folder) in enumerate(self.temp_folders.items()):
            row = i * 2 + 1  # jede Section braucht 2 Zeilen
            # Title Label
            title_label = ctk.CTkLabel(btn_frame, text=name, anchor="w")
            title_label.grid(row=row, column=0, sticky="w", padx=5)

            # Delete Button
            btn = ctk.CTkButton(
                btn_frame,
                text="Delete",
                command=lambda f=folder: self.delete_folder(f)
            )
            btn.grid(row=row, column=1, sticky="e", padx=5)

            # Description Label
            desc_label = ctk.CTkLabel(btn_frame, text=folder, anchor="w", fg_color="transparent")
            desc_label.grid(row=row + 1, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))

            self.temp_buttons[name] = {"button": btn, "folder": folder}

        # -------------------------
        # PROJECT ACTION BUTTONS
        # -------------------------
        self.project_buttons = {}
        project_actions = [
            ("Open in Unreal", self.open_unreal, ["unreal", "unreal_project_file"]),
            ("Open in Visual Studio", self.open_vs, ["sln_file", "visual_studio"]),
            ("Open in VSCode", self.open_vscode, ["unreal_project", "vscode"]),
            ("Open Project Folder", self.open_explorer, ["unreal_project"]),
            ("Open in Terminal", self.open_terminal, ["unreal_project"])
        ]

        start_row = len(self.temp_folders) * 2 + 1
        for i, (label, func, keys) in enumerate(project_actions):
            row = start_row + (i // 3)
            col = i % 3
            btn = ctk.CTkButton(
                btn_frame,
                text=label,
                command=func
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.project_buttons[label] = {"button": btn, "keys": keys}

        # Start live updates
        self._update_buttons()

    # -------------------------
    # HELPER METHODS
    # -------------------------
    def _paths_exist(self, keys):
        for key in keys:
            path = self.paths.get(key)
            if not path or not os.path.exists(path):
                return False
        return True

    def _get_temp_folders(self):
        project = self.paths.get("unreal_project")
        if not project:
            return {}

        user = os.getenv("USERNAME")
        global_ddc = f"C:/Users/{user}/AppData/Local/UnrealEngine/Common/DerivedDataCache"

        folders = {
            "Intermediate": os.path.join(project, "Intermediate"),
            "Saved": os.path.join(project, "Saved"),
            "DerivedDataCache_Project": os.path.join(project, "DerivedDataCache"),
            "Binaries": os.path.join(project, "Binaries"),
            ".vs": os.path.join(project, ".vs"),
            "DerivedDataCache_Global": global_ddc
        }
        LOGGER.debug(f"{folders=}")
        return folders

    # -------------------------
    # DELETE METHODS
    # -------------------------
    def delete_folder(self, folder):
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                LOGGER.info(f"Deleted: {folder}")
            except Exception as e:
                LOGGER.error(f"Error deleting {folder}: {e}")
        else:
            LOGGER.error(f"Folder does not exist: {folder}")

    def delete_all_temp(self):
        for folder in self.temp_folders.values():
            self.delete_folder(folder)

    # -------------------------
    # LIVE UPDATE FOR BUTTONS
    # -------------------------
    def _update_buttons(self):
        # Temp folders buttons
        for info in self.temp_buttons.values():
            btn = info["button"]
            folder = info["folder"]
            if os.path.exists(folder):
                btn.configure(state="normal", fg_color="#187e18")
            else:
                btn.configure(state="disabled", fg_color="#8a0000")

        # Project buttons
        for info in self.project_buttons.values():
            btn = info["button"]
            keys = info["keys"]
            if self._paths_exist(keys):
                btn.configure(state="normal", fg_color="#187e18")
            else:
                btn.configure(state="disabled", fg_color="#8a0000")

        # Repeat every 10 seconds
        self.after(10000, self._update_buttons)

    # -------------------------
    # PROJECT ACTIONS
    # -------------------------
    def open_unreal(self):
        subprocess.Popen([self.paths["unreal"], self.paths["unreal_project_file"]])

    def open_vs(self):
        subprocess.Popen([self.paths["visual_studio"], self.paths["sln_file"]])

    def open_vscode(self):
        subprocess.Popen([self.paths["vscode"], self.paths["unreal_project"]])

    def open_explorer(self):
        subprocess.Popen(["explorer", self.paths["unreal_project"]])

    def open_terminal(self):
        subprocess.Popen(
            ["cmd", "/c", f"start cmd /K cd /d {self.paths['unreal_project']}"]
        )


