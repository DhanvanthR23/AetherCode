import customtkinter as ctk

class FileExplorerContextMenu(ctk.CTkToplevel):
    def __init__(self, master, app_window):
        super().__init__(master)
        self.app_window = app_window
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.withdraw()  # Hide the window initially
        self.overrideredirect(True) # Remove window decorations

        self.menu_frame = ctk.CTkFrame(self, corner_radius=5, border_width=1)
        self.menu_frame.pack()

        self.add_command("New File", self.new_file)
        self.add_command("New Folder", self.new_folder)
        self.add_separator()
        self.add_command("Rename", self.rename_item)
        self.add_command("Delete", self.delete_item)

        self.bind("<FocusOut>", lambda e: self.withdraw())


    def add_command(self, label, command):
        button = ctk.CTkButton(self.menu_frame, text=label, corner_radius=0, command=lambda: self.on_command(command), anchor="w")
        button.pack(fill="x", padx=5, pady=2)

    def add_separator(self):
        separator = ctk.CTkFrame(self.menu_frame, height=1, border_width=0, fg_color="gray50")
        separator.pack(fill="x", padx=5, pady=2)

    def on_command(self, command):
        self.withdraw()
        command()

    def popup(self, event, path):
        self.current_path = path
        self.geometry(f"+{event.x_root}+{event.y_root}")
        self.deiconify()
        self.lift()
        self.focus_set()

    def new_file(self):
        self.app_window._create_new_item(self.current_path, item_type="file")

    def new_folder(self):
        self.app_window._create_new_item(self.current_path, item_type="folder")

    def rename_item(self):
        self.app_window._rename_item(self.current_path)

    def delete_item(self):
        self.app_window._delete_item(self.current_path)
