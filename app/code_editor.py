import customtkinter as ctk
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

class CodeEditor(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.dracula_theme = {
            "background": "#282a36",
            "current_line": "#44475a",
            "foreground": "#f8f8f2",
            "comment": "#6272a4",
            "cyan": "#8be9fd",
            "green": "#50fa7b",
            "orange": "#ffb86c",
            "pink": "#ff79c6",
            "purple": "#bd93f9",
            "red": "#ff5555",
            "yellow": "#f1fa8c"
        }
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text_editor = ctk.CTkTextbox(self, wrap="none", font=("monospace", 16), fg_color=self.dracula_theme["background"], text_color=self.dracula_theme["foreground"])
        self.text_editor.grid(row=0, column=0, sticky="nsew")

        # --- TAGS FOR SYNTAX HIGHLIGHTING ---
        self.text_editor.tag_config("Token.Keyword", foreground=self.dracula_theme["pink"])
        self.text_editor.tag_config("Token.Keyword.Constant", foreground=self.dracula_theme["purple"])
        self.text_editor.tag_config("Token.Keyword.Namespace", foreground=self.dracula_theme["pink"])
        self.text_editor.tag_config("Token.Name.Builtin", foreground=self.dracula_theme["cyan"])
        self.text_editor.tag_config("Token.Name.Function", foreground=self.dracula_theme["green"])
        self.text_editor.tag_config("Token.Name.Class", foreground=self.dracula_theme["cyan"])
        self.text_editor.tag_config("Token.String", foreground=self.dracula_theme["yellow"])
        self.text_editor.tag_config("Token.String.Doc", foreground=self.dracula_theme["comment"])
        self.text_editor.tag_config("Token.Comment", foreground=self.dracula_theme["comment"])
        self.text_editor.tag_config("Token.Number", foreground=self.dracula_theme["purple"])
        self.text_editor.tag_config("Token.Operator", foreground=self.dracula_theme["pink"])
        self.text_editor.tag_config("Token.Punctuation", foreground=self.dracula_theme["foreground"])

        # --- BIND TO KEY RELEASE ---
        self.text_editor.bind("<KeyRelease>", self.on_key_release)

    def get(self, *args, **kwargs):
        """Pass get method to the underlying text editor."""
        return self.text_editor.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        """Pass insert method to the underlying text editor."""
        self.text_editor.insert(*args, **kwargs)
        self.on_key_release() # Trigger highlighting on insert

    def delete(self, *args, **kwargs):
        """Pass delete method to the underlying text editor."""
        self.text_editor.delete(*args, **kwargs)

    def get_content(self) -> str:
        """Returns all text content from the editor."""
        return self.text_editor.get("1.0", "end-1c")

    def on_key_release(self, event=None):
        """Handles syntax highlighting when a key is released."""
        self.highlight_syntax()

    def highlight_syntax(self):
        """Applies syntax highlighting to the text in the editor."""
        text_content = self.get_content()
        # Remove all existing tags
        for tag in self.text_editor.tag_names():
            if tag.startswith("Token"):
                self.text_editor.tag_remove(tag, "1.0", "end")

        # Add new tags
        current_pos = "1.0"
        for token, content in lex(text_content, PythonLexer()):
            end_pos = f"{current_pos} + {len(content)}c"
            self.text_editor.tag_add(str(token), current_pos, end_pos)
            current_pos = end_pos
