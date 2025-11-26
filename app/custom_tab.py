import customtkinter as ctk
from .code_editor import CodeEditor

class CustomTab(ctk.CTkFrame):
    def __init__(self, master, title, close_callback):
        super().__init__(master, fg_color="transparent")
        self.title = title
        self.close_callback = close_callback

        self.grid_rowconfigure(0, weight=0)  # Header row
        self.grid_rowconfigure(1, weight=1)  # Editor row
        self.grid_columnconfigure(0, weight=1)

        # Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self.header_frame, text=title)
        self.label.grid(row=0, column=0, sticky="w", padx=(5,0))

        self.close_button = ctk.CTkButton(self.header_frame, text="x", width=20, height=20, corner_radius=0, command=self.close)
        
        # Event binding
        self.header_frame.bind("<Enter>", self.show_close_button)
        self.label.bind("<Enter>", self.show_close_button)
        self.header_frame.bind("<Leave>", self.hide_close_button)
        self.label.bind("<Leave>", self.hide_close_button)
        
    def add_code_editor(self):
        code_editor = CodeEditor(self, corner_radius=0)
        code_editor.grid(row=1, column=0, sticky="nsew") # Place editor in row 1
        return code_editor

    def show_close_button(self, event=None):
        self.close_button.grid(row=0, column=1, sticky="e")

    def hide_close_button(self, event=None):
        # Check if the mouse is over the close button itself
        if event and self.close_button.winfo_containing(event.x_root, event.y_root) == self.close_button:
             return
        self.close_button.grid_forget()

    def close(self):
        self.close_callback(self.title)
