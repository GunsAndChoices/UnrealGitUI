import os
import shutil
import subprocess
from CTkTable import CTkTable
import customtkinter as ctk
import threading

from main.config import load_config
from main._template import LOGGER
from main.ctk_external_modules.CTkCollapsibleFrame import CTkCollapsiblePanel


CONFIG = load_config("main/config.json")


class UnrealToolsUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.paths = CONFIG.get("paths", {})
        self.buttons = {} 
        self.tick = "✔"
        self.cross = "✘"

        # ===== TITLE =====
        title = ctk.CTkLabel(self, text="Unreal Engine Tools", font=("Segoe UI", 24, "bold"))
        title.pack(pady=(10, 15), fill="x")
        
        # ===== FOUND ENTRIES =====
        found_frame = ctk.CTkFrame(self)
        found_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        data = [[]]
        names = {
                                "unreal": "Unreal",
                                "unreal_project_file": "Unreal File",
                                "sln_file": "SLN File",
                                "vscode": "VSCode",
                                "unreal_project": "Unreal Project",
                                "visual_studio": "Visual Studio"
                            }
        for key, path in self.paths.items():
            if self._paths_exist([key]):
                data[0].append(f"{self.tick} {names.get(key, key.replace('_', ' ').title())}")
            else:
                data[0].append(f"{self.cross} {names.get(key, key.replace('_', ' ').title())}")
        
        entries_table = CTkTable(
            found_frame, 
            values=data, 
            row= len(data)
        )
        entries_table.pack(fill="both", padx=5, pady=5, expand=True)
        
        # ===== PROJECT ACTIONS =====
        project_panel = CTkCollapsiblePanel(self, title="Project Actions")
        project_panel.pack(fill="x", padx=15, pady=(0, 10))

        project_actions = [
            ("Open in Unreal", self.open_unreal, ["unreal", "unreal_project_file"]),
            ("Open in Visual Studio", self.open_vs, ["sln_file"]),
            ("Open in VSCode", self.open_vscode, ["unreal_project", "vscode"]),
            ("Open Project Folder", self.open_explorer, ["unreal_project"]),
            ("Open in Terminal", self.open_terminal, ["unreal_project"])
        ]

        for label, func, keys in project_actions:
            btn = ctk.CTkButton(project_panel._content_frame, text=label, command=func)
            btn.pack(fill="x", padx=5, pady=5)
            self.buttons[label] = {"button": btn, "keys": keys}

        # ===== BUILD TOOLS =====
        build_panel = CTkCollapsiblePanel(self, title="Build Tools")
        build_panel.pack(fill="x", padx=15, pady=(0, 10))

        build_actions = [
            ("Generate Project Files", self.generate_project_files, ["unreal", "unreal_project_file"]),
            ("Build Project", self.build_project, ["sln_file"]),
        ]

        for label, func, keys in build_actions:
            btn = ctk.CTkButton(build_panel._content_frame, text=label, command=func)
            btn.pack(fill="x", padx=5, pady=5)
            self.buttons[label] = {"button": btn, "keys": keys}

        # ===== CONFIGURATION =====
        config_panel = CTkCollapsiblePanel(self, title="Configuration Files")
        config_panel.pack(fill="x", padx=15, pady=(0, 10))

        config_files = ["DefaultEngine.ini", "DefaultGame.ini", "DefaultInput.ini"]
        for f in config_files:
            btn = ctk.CTkButton(config_panel._content_frame, text=f"Open {f}")
            btn.configure(command=lambda name=f: self.open_config_file(name))
            btn.pack(fill="x", padx=5, pady=5)
            # The key for the button is the filename itself for the update logic
            self.buttons[f] = {"button": btn, "keys": ["unreal_project"]}
            
        # ===== TEMPORARY DATA =====
        temp_panel = CTkCollapsiblePanel(self, title="Temporary Data")
        temp_panel.pack(fill="x", padx=15, pady=(0, 10))
        
        self.temp_folders = self._get_temp_folders()
        self.temp_buttons = {}

        for name, folder in self.temp_folders.items():
            btn = ctk.CTkButton(temp_panel._content_frame, text=name)
            btn.configure(command=lambda f=folder, b=btn, n=name: self.delete_folder_threaded(f, b, n))
            btn.pack(fill="x", padx=5, pady=5)
            self.temp_buttons[name] = {"button": btn, "folder": folder}

        delete_all_btn_text = "Delete All Temporary Data"
        delete_all_btn = ctk.CTkButton(temp_panel._content_frame, text=delete_all_btn_text)
        delete_all_btn.configure(command=lambda: self.delete_all_temp_threaded(delete_all_btn, delete_all_btn_text))
        delete_all_btn.pack(fill="x", padx=5, pady=8)
        self.temp_buttons["Delete All"] = {"button": delete_all_btn, "folder": "any"} # Special case

        # Start live updates
        self._update_button_states()

    # ===== HELPERS =====
    def _paths_exist(self, keys):
        for key in keys:
            path = self.paths.get(key)
            if not path or not os.path.exists(path):
                return False
        return True

    def _get_temp_folders(self):
        project_path = self.paths.get("unreal_project")
        if not project_path: return {}
        user = os.getenv("USERNAME")
        return {
            "Intermediate": os.path.join(project_path, "Intermediate"),
            "Saved": os.path.join(project_path, "Saved"),
            "DerivedDataCache": os.path.join(project_path, "DerivedDataCache"),
            "Binaries": os.path.join(project_path, "Binaries"),
            ".vs": os.path.join(project_path, ".vs"),
            "Global DDC": f"C:/Users/{user}/AppData/Local/UnrealEngine/Common/DerivedDataCache",
        }

    # ===== ASYNC TASK WRAPPERS =====
    def run_threaded_task(self, task_func, on_complete=None):
        def task_wrapper():
            task_func()
            if on_complete:
                self.after(0, on_complete)
        threading.Thread(target=task_wrapper, daemon=True).start()

    def delete_folder_threaded(self, folder_path, button, original_text):
        button.configure(state="disabled", text="Deleting...")
        task = lambda: self.delete_folder(folder_path)
        on_complete = lambda: self.on_delete_finished(button, original_text)
        self.run_threaded_task(task, on_complete)

    def delete_all_temp_threaded(self, button, original_text):
        button.configure(state="disabled", text="Deleting...")
        on_complete = lambda: self.on_delete_finished(button, original_text)
        self.run_threaded_task(self.delete_all_temp, on_complete)
        
    def on_delete_finished(self, button, original_text):
        button.configure(text=original_text)
        self._update_button_states()

    # ===== DELETE METHODS =====
    def delete_folder(self, folder_path):
        LOGGER.info(f"Attempting to delete folder: {folder_path}")
        if not os.path.exists(folder_path):
            LOGGER.warning(f"Folder not found, cannot delete: {folder_path}")
            return
        try:
            shutil.rmtree(folder_path)
            LOGGER.info(f"Successfully deleted: {folder_path}")
        except Exception as e:
            LOGGER.error(f"Error deleting {folder_path}: {e}")

    def delete_all_temp(self):
        for folder in self.temp_folders.values():
            self.delete_folder(folder)

    # ===== BUTTON STATE UPDATE =====
    def _update_button_states(self):
        # Temp folder buttons: Green if exists (deletable), Red if not
        for name, info in self.temp_buttons.items():
            if name == "Delete All": continue # Handled separately
            exists = os.path.exists(info["folder"])
            state = "normal" if exists else "disabled"
            color = "#b83b3b" if exists else "#565b5f" # Red for danger, gray for disabled
            info["button"].configure(state=state, fg_color=color)
        
        # "Delete All" button is active if any temp folder exists
        any_temp_exists = any(os.path.exists(f) for f in self.temp_folders.values())
        all_btn_state = "normal" if any_temp_exists else "disabled"
        all_btn_color = "#b83b3b" if any_temp_exists else "#565b5f"
        self.temp_buttons["Delete All"]["button"].configure(state=all_btn_state, fg_color=all_btn_color)

        # General action buttons: Green if available, Gray if not
        for name, info in self.buttons.items():
            if ".ini" in name:
                proj_path = self.paths.get("unreal_project", "")
                exists = proj_path and os.path.exists(os.path.join(proj_path, "Config", name))
            else:
                exists = self._paths_exist(info["keys"])
            state = "normal" if exists else "disabled"
            color = "#1f6aa5" if exists else "#565b5f"
            info["button"].configure(state=state, fg_color=color)

        self.after(5000, self._update_button_states)

    # ===== PROJECT ACTIONS =====
    def open_unreal(self):
        self.run_threaded_task(lambda: subprocess.Popen(
            [self.paths["unreal"], self.paths["unreal_project_file"]]
        ))

    def open_vs(self):
        self.run_threaded_task(lambda: os.startfile(self.paths["sln_file"]))

    def open_vscode(self):
        self.run_threaded_task(lambda: subprocess.Popen(
            [self.paths["vscode"], self.paths["unreal_project"]]
        ))

    def open_explorer(self):
        subprocess.Popen(["explorer", self.paths["unreal_project"]])

    def open_terminal(self):
        # This doesn't need a thread as it's instant
        subprocess.Popen(["cmd", "/K", f"cd /d {self.paths['unreal_project']}"])

    def open_config_file(self, file_name):
        config_path = os.path.join(self.paths.get("unreal_project", ""), "Config", file_name)
        if os.path.exists(config_path):
            self.run_threaded_task(lambda: os.startfile(config_path))
        else:
            LOGGER.error(f"Config file not found: {config_path}")

    # ===== BUILD ACTIONS =====
    def generate_project_files(self):
        LOGGER.info("Starting: Generate project files...")
        cmd = [self.paths["unreal"], self.paths["unreal_project_file"], "-projectfiles"]
        self.run_threaded_task(lambda: subprocess.run(cmd, capture_output=True))
        LOGGER.info("Completed: Generate project files.")

    def build_project(self):
        LOGGER.info("Starting: Build project...")
        sln_path = self.paths.get("sln_file")
        if not sln_path or not os.path.exists(sln_path):
            LOGGER.error("Could not find .sln file to build.")
            return
        
        # Assumes MSBuild is in PATH. A more robust solution would be to find it.
        cmd = [
            "msbuild", sln_path, 
            "/p:Configuration=Development Editor", 
            "/p:Platform=Win64", "/t:build"
        ]
        self.run_threaded_task(lambda: subprocess.run(cmd, capture_output=True))
        LOGGER.info("Completed: Build project. Check logs for status.")

