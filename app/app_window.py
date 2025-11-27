import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import subprocess
import sys
import tempfile
import os
import shutil
from .ai_service import AIService
from .code_editor import CodeEditor
from .custom_tab import CustomTab
from .file_explorer_context_menu import FileExplorerContextMenu

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AetherCode")
        self.geometry("1400x900")
        
        # --- Theme ---
        ctk.set_appearance_mode("dark")
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
        self.configure(fg_color=self.dracula_theme["background"])
        self.tab_file_paths = {}

        # --- Main Layout ---
        self.grid_rowconfigure(0, weight=0)  # Menu bar
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)  # File explorer
        self.grid_columnconfigure(1, weight=4)  # Main content
        self.grid_columnconfigure(2, weight=1)  # AI Panel

        # --- File Explorer ---
        self.file_explorer_frame = ctk.CTkFrame(self, corner_radius=0, width=250, fg_color="#21222c")
        self.file_explorer_frame.grid(row=1, column=0, sticky="nsew")
        self.file_explorer_frame.grid_rowconfigure(1, weight=1)
        self.file_explorer_frame.grid_columnconfigure(0, weight=1)
        self.file_explorer_label = ctk.CTkLabel(self.file_explorer_frame, text="File Explorer", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.dracula_theme["purple"])
        self.file_explorer_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.current_dir = None
        self._populate_file_explorer(os.getcwd())

        # --- Main Content ---
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=1, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=3)
        self.main_content_frame.grid_rowconfigure(1, weight=0)
        self.main_content_frame.grid_rowconfigure(2, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self.main_content_frame, fg_color="#21222c", segmented_button_fg_color=self.dracula_theme["background"], segmented_button_selected_color=self.dracula_theme["current_line"], segmented_button_unselected_color=self.dracula_theme["background"])
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self._add_tab("Untitled")
        
        self.new_tab_button = ctk.CTkButton(self.main_content_frame, text="+", width=30, command=self._new_file, fg_color=self.dracula_theme["green"], text_color=self.dracula_theme["background"], hover_color="#45a049")
        self.new_tab_button.place(in_=self.tab_view, relx=1.0, x=-35, y=5, anchor="ne")


        self.output_frame = ctk.CTkFrame(self.main_content_frame, corner_radius=0, fg_color="#21222c", height=200)
        self.output_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.output_frame.grid_rowconfigure(0, weight=0) # Output label row
        self.output_frame.grid_rowconfigure(1, weight=1) # Output console row
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_label = ctk.CTkLabel(self.output_frame, text="Output", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.dracula_theme["cyan"])
        self.output_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.output_console = ctk.CTkTextbox(self.output_frame, wrap="word", state="disabled", font=("monospace", 13), fg_color="#282a36", text_color=self.dracula_theme["foreground"])
        self.output_console.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- AI Controls ---
        self.controls_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#21222c")
        self.controls_frame.grid(row=1, column=2, sticky="nsew")
        self.controls_frame.grid_rowconfigure(7, weight=1)
        self.controls_frame.grid_columnconfigure(0, weight=1)
        
        # --- AI Controls (continued)
        self.run_button = ctk.CTkButton(self.controls_frame, text="Run Code", command=self._run_code, fg_color=self.dracula_theme["green"], text_color=self.dracula_theme["background"], hover_color="#45a049")
        self.run_button.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
        self.mode_label = ctk.CTkLabel(self.controls_frame, text="AI Mode", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.dracula_theme["pink"])
        self.mode_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.mode_selection = ctk.CTkSegmentedButton(self.controls_frame, values=["Generator", "Mentor"], selected_color=self.dracula_theme["pink"], unselected_color=self.dracula_theme["current_line"])
        self.mode_selection.set("Mentor")
        self.mode_selection.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.prompt_label = ctk.CTkLabel(self.controls_frame, text="Your Request/Question", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.dracula_theme["orange"])
        self.prompt_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.prompt_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="e.g., 'create a function to sum a list'", fg_color=self.dracula_theme["current_line"], border_color=self.dracula_theme["current_line"])
        self.prompt_entry.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.submit_button = ctk.CTkButton(self.controls_frame, text="Get AI Assistance", command=self._on_submit_ai, fg_color=self.dracula_theme["purple"], hover_color="#a47de1")
        self.submit_button.grid(row=5, column=0, padx=10, pady=20, sticky="ew")
        self.mentor_output_label = ctk.CTkLabel(self.controls_frame, text="Mentor Output", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.dracula_theme["yellow"])
        self.mentor_output_label.grid(row=6, column=0, padx=10, pady=5, sticky="nw")
        self.mentor_output = ctk.CTkTextbox(self.controls_frame, wrap="word", state="disabled", fg_color=self.dracula_theme["current_line"])
        self.mentor_output.grid(row=7, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.ai_service = AIService()
        self._setup_menubar()
        self.file_explorer_context_menu = FileExplorerContextMenu(self, self)
        
    def _show_context_menu(self, event, path):
        self.file_explorer_context_menu.popup(event, path)

    def _create_new_item(self, path, item_type):
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        dialog = ctk.CTkInputDialog(text=f"Enter name for new {item_type}:", title=f"Create {item_type.capitalize()}")
        name = dialog.get_input()

        if name:
            new_path = os.path.join(path, name)
            try:
                if item_type == "file":
                    with open(new_path, "w") as f:
                        f.write("")
                elif item_type == "folder":
                    os.makedirs(new_path)
                self._populate_file_explorer(self.current_dir)
            except Exception as e:
                self.output_console.configure(state="normal")
                self.output_console.delete("1.0", "end")
                self.output_console.insert("1.0", f"Error creating {item_type}: {e}")
                self.output_console.configure(state="disabled")


    def _rename_item(self, path):
        dialog = ctk.CTkInputDialog(text="Enter new name:", title="Rename")
        new_name = dialog.get_input()

        if new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self._populate_file_explorer(self.current_dir)
            except Exception as e:
                self.output_console.configure(state="normal")
                self.output_console.delete("1.0", "end")
                self.output_console.insert("1.0", f"Error renaming item: {e}")
                self.output_console.configure(state="disabled")

    def _delete_item(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            self._populate_file_explorer(self.current_dir)
        except Exception as e:
            self.output_console.configure(state="normal")
            self.output_console.delete("1.0", "end")
            self.output_console.insert("1.0", f"Error deleting item: {e}")
            self.output_console.configure(state="disabled")

    def _setup_menubar(self):
        self.menu_bar = ctk.CTkFrame(self, corner_radius=0, height=30)
        self.menu_bar.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.file_menu_button = ctk.CTkButton(self.menu_bar, text="File", corner_radius=0, command=self._show_file_menu)
        self.file_menu_button.pack(side="left")

        self.edit_menu_button = ctk.CTkButton(self.menu_bar, text="Edit", corner_radius=0, command=self._show_edit_menu)
        self.edit_menu_button.pack(side="left")

        self.run_menu_button = ctk.CTkButton(self.menu_bar, text="Run", corner_radius=0, command=self._show_run_menu)
        self.run_menu_button.pack(side="left")

        self._create_file_menu()
        self._create_edit_menu()
        self._create_run_menu()

        self.bind_all("<Button-1>", self._hide_menus)

    def _create_file_menu(self):
        self.file_menu = ctk.CTkFrame(self, corner_radius=0)
        
        new_file_button = ctk.CTkButton(self.file_menu, text="New File (Ctrl+N)", corner_radius=0, command=self._new_file)
        new_file_button.pack(fill="x")
        
        open_button = ctk.CTkButton(self.file_menu, text="Open (Ctrl+O)", corner_radius=0, command=self._open_file)
        open_button.pack(fill="x")

        open_folder_button = ctk.CTkButton(self.file_menu, text="Open Folder", corner_radius=0, command=self._open_folder)
        open_folder_button.pack(fill="x")
        
        save_button = ctk.CTkButton(self.file_menu, text="Save (Ctrl+S)", corner_radius=0, command=self._save_file)
        save_button.pack(fill="x")

        save_as_button = ctk.CTkButton(self.file_menu, text="Save As (Ctrl+Shift+S)", corner_radius=0, command=self._save_as_file)
        save_as_button.pack(fill="x")
        
        exit_button = ctk.CTkButton(self.file_menu, text="Exit", corner_radius=0, command=self.quit)
        exit_button.pack(fill="x")

        self.bind("<Control-n>", self._new_file)
        self.bind("<Control-o>", self._open_file)
        self.bind("<Control-s>", self._save_file)
        self.bind("<Control-Shift-S>", self._save_as_file)

    def _create_edit_menu(self):
        self.edit_menu = ctk.CTkFrame(self, corner_radius=0)
        
        cut_button = ctk.CTkButton(self.edit_menu, text="Cut", corner_radius=0, command=self._cut_text)
        cut_button.pack(fill="x")
        
        copy_button = ctk.CTkButton(self.edit_menu, text="Copy", corner_radius=0, command=self._copy_text)
        copy_button.pack(fill="x")
        
        paste_button = ctk.CTkButton(self.edit_menu, text="Paste", corner_radius=0, command=self._paste_text)
        paste_button.pack(fill="x")

    def _create_run_menu(self):
        self.run_menu = ctk.CTkFrame(self, corner_radius=0)
        
        run_button = ctk.CTkButton(self.run_menu, text="Run Code", corner_radius=0, command=self._run_code)
        run_button.pack(fill="x")

    def _show_file_menu(self):
        if self.file_menu.winfo_ismapped():
            self.file_menu.place_forget()
        else:
            self.file_menu.place(in_=self.file_menu_button, relx=0, rely=1.0)
            self.file_menu.lift()
            self.edit_menu.place_forget()
            self.run_menu.place_forget()

    def _show_edit_menu(self):
        if self.edit_menu.winfo_ismapped():
            self.edit_menu.place_forget()
        else:
            self.edit_menu.place(in_=self.edit_menu_button, relx=0, rely=1.0)
            self.edit_menu.lift()
            self.file_menu.place_forget()
            self.run_menu.place_forget()

    def _show_run_menu(self):
        if self.run_menu.winfo_ismapped():
            self.run_menu.place_forget()
        else:
            self.run_menu.place(in_=self.run_menu_button, relx=0, rely=1.0)
            self.run_menu.lift()
            self.file_menu.place_forget()
            self.edit_menu.place_forget()
    
    def _hide_menus(self, event=None):
        if event and (self.file_menu_button.winfo_containing(event.x_root, event.y_root) == self.file_menu_button or
                     self.edit_menu_button.winfo_containing(event.x_root, event.y_root) == self.edit_menu_button or
                     self.run_menu_button.winfo_containing(event.x_root, event.y_root) == self.run_menu_button or
                     self.file_menu.winfo_containing(event.x_root, event.y_root) or
                     self.edit_menu.winfo_containing(event.x_root, event.y_root) or
                     self.run_menu.winfo_containing(event.x_root, event.y_root)):
            return

        self.file_menu.place_forget()
        self.edit_menu.place_forget()
        self.run_menu.place_forget()


    def _new_file(self, event=None):
        untitled_count = 1
        new_tab_name = "Untitled"
        while new_tab_name in self.tab_view._tab_dict.keys():
            untitled_count += 1
            new_tab_name = f"Untitled-{untitled_count}"
        self._add_tab(new_tab_name)

    def _add_tab(self, title, file_path=None):
        self.tab_view.add(title)
        self.tab_file_paths[title] = file_path
        
        custom_tab = CustomTab(self.tab_view.tab(title), title, self._close_tab)
        custom_tab.pack(fill="both", expand=True)

        code_editor = custom_tab.add_code_editor()
        return code_editor

    def _close_tab(self, title):
        if title in self.tab_file_paths:
            del self.tab_file_paths[title]
        self.tab_view.delete(title)


    def _save_file(self, event=None):
        current_tab_name = self.tab_view.get()
        if not current_tab_name:
            return

        file_path = self.tab_file_paths.get(current_tab_name)
        editor = self._get_current_editor()
        if not editor:
            return

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(editor.get("1.0", "end-1c"))
                self.title(f"AetherCode - {os.path.basename(file_path)}")
            except Exception as e:
                self.output_console.configure(state="normal")
                self.output_console.delete("1.0", "end")
                self.output_console.insert("1.0", f"Error saving file: {e}")
                self.output_console.configure(state="disabled")
        else:
            self._save_as_file()

    def _save_as_file(self, event=None):
        current_tab_name = self.tab_view.get()
        if not current_tab_name:
            return

        editor = self._get_current_editor()
        if not editor:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            content = editor.get("1.0", "end-1c")
            
            # Close the old tab if it's an "Untitled" tab
            if self.tab_file_paths.get(current_tab_name) is None:
                self.tab_view.delete(current_tab_name)
                if current_tab_name in self.tab_file_paths:
                    del self.tab_file_paths[current_tab_name]

            new_tab_name = os.path.basename(file_path)
            
            # If a tab for this file path already exists, switch to it
            for tab, path in self.tab_file_paths.items():
                if path == file_path:
                    self.tab_view.set(tab)
                    self._get_current_editor().delete("1.0", "end")
                    self._get_current_editor().insert("1.0", content)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return
            
            # Create a new tab for the saved file
            new_editor = self._add_tab(new_tab_name, file_path=file_path)
            new_editor.insert("1.0", content)
            self.tab_view.set(new_tab_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.title(f"AetherCode - {new_tab_name}")
            
        except Exception as e:
            self.output_console.configure(state="normal")
            self.output_console.delete("1.0", "end")
            self.output_console.insert("1.0", f"Error saving file: {e}")
            self.output_console.configure(state="disabled")

    def _cut_text(self):
        editor = self._get_current_editor()
        if editor:
            editor.event_generate("<<Cut>>")

    def _copy_text(self):
        editor = self._get_current_editor()
        if editor:
            editor.event_generate("<<Copy>>")

    def _paste_text(self):
        editor = self._get_current_editor()
        if editor:
            editor.event_generate("<<Paste>>")

    def _populate_file_explorer(self, directory):
        try:
            for widget in self.file_explorer_frame.winfo_children():
                if widget != self.file_explorer_label:
                    widget.destroy()

            for i in range(self.file_explorer_frame.grid_size()[1]):
                self.file_explorer_frame.grid_rowconfigure(i, weight=0)
            
            self.current_dir = directory
            self.file_explorer_label.configure(text=f"Explorer: {os.path.basename(directory)}")
            self.file_explorer_frame.grid_rowconfigure(0, weight=0)

            parent_dir = os.path.dirname(directory)
            row_index = 1
            if parent_dir != directory:
                parent_label = ctk.CTkLabel(self.file_explorer_frame, text=".. (Parent)", text_color="cyan", cursor="hand2")
                parent_label.grid(row=1, column=0, padx=10, pady=2, sticky="ew")
                parent_label.bind("<Button-1>", lambda e, p=parent_dir: self._on_directory_click(p))
                parent_label.bind("<Button-3>", lambda e, p=parent_dir: self._show_context_menu(e, p))
                self.file_explorer_frame.grid_rowconfigure(1, weight=0)
                row_index = 2

            items = sorted(os.listdir(directory))
            dirs = [item for item in items if os.path.isdir(os.path.join(directory, item))]
            files = [item for item in items if os.path.isfile(os.path.join(directory, item))]

            for item in dirs:
                path = os.path.join(directory, item)
                label = ctk.CTkLabel(self.file_explorer_frame, text=f"📁 {item}", cursor="hand2")
                label.grid(row=row_index, column=0, padx=10, pady=2, sticky="ew")
                label.bind("<Button-1>", lambda e, p=path: self._on_directory_click(p))
                label.bind("<Button-3>", lambda e, p=path: self._show_context_menu(e, p))
                self.file_explorer_frame.grid_rowconfigure(row_index, weight=0)
                row_index += 1

            for item in files:
                path = os.path.join(directory, item)
                label = ctk.CTkLabel(self.file_explorer_frame, text=f"📄 {item}", cursor="hand2")
                label.grid(row=row_index, column=0, padx=10, pady=2, sticky="ew")
                label.bind("<Button-1>", lambda e, p=path: self._on_file_click(p))
                label.bind("<Button-3>", lambda e, p=path: self._show_context_menu(e, p))
                self.file_explorer_frame.grid_rowconfigure(row_index, weight=0)
                row_index += 1
            
            if row_index > 0:
                self.file_explorer_frame.grid_rowconfigure(row_index, weight=1)

        except Exception as e:
            self.output_console.configure(state="normal")
            self.output_console.delete("1.0", "end")
            self.output_console.insert("1.0", f"Error populating file explorer: {e}")
            self.output_console.configure(state="disabled")

    def _get_current_editor(self):
        current_tab_name = self.tab_view.get()
        if current_tab_name:
            tab = self.tab_view.tab(current_tab_name)
            if tab.winfo_children():
                custom_tab = tab.winfo_children()[0]
                # The add_code_editor method in CustomTab creates the CodeEditor, which is a child of CustomTab
                # and is the second child of the CustomTab frame after the header.
                # Since we know the structure, we can directly access it.
                # A more robust way would be to iterate and check isinstance, but this is faster.
                for child in custom_tab.winfo_children():
                    if isinstance(child, CodeEditor):
                        return child
        return None

    def _on_directory_click(self, path):
        self._populate_file_explorer(path)

    def _on_file_click(self, path):
        try:
            # Check if the file is already open
            for tab_name, file_path in self.tab_file_paths.items():
                if file_path == path:
                    self.tab_view.set(tab_name)
                    return
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            new_tab_name = os.path.basename(path)
            editor = self._add_tab(new_tab_name, file_path=path)
            editor.insert("1.0", content)
            self.tab_view.set(new_tab_name)
            self.title(f"AetherCode - {new_tab_name}")
        except Exception as e:
            self.output_console.configure(state="normal")
            self.output_console.delete("1.0", "end")
            self.output_console.insert("1.0", f"Error opening file: {e}")
            self.output_console.configure(state="disabled")

    def _open_file(self, event=None):
        self.unbind_all("<Button-1>")
        file_path = filedialog.askopenfilename()
        self.bind_all("<Button-1>", self._hide_menus)
        if file_path:
            self._on_file_click(file_path)

    def _open_folder(self, event=None):
        self.unbind_all("<Button-1>")
        folder_path = filedialog.askdirectory()
        self.bind_all("<Button-1>", self._hide_menus)
        if folder_path:
            self._populate_file_explorer(folder_path)


    def _run_code(self):
        editor = self._get_current_editor()
        if editor:
            code = editor.get("1.0", "end-1c")
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                process = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                stdout = process.stdout
                stderr = process.stderr
            except subprocess.CalledProcessError as e:
                stdout = e.stdout
                stderr = e.stderr
            finally:
                os.unlink(temp_file_path)

            self.output_console.configure(state="normal")
            self.output_console.delete("1.0", "end")
            self.output_console.insert("1.0", "--- STDOUT ---\n")
            self.output_console.insert("end", stdout)
            if stderr:
                self.output_console.insert("end", "\n--- STDERR ---\n")
                self.output_console.insert("end", stderr)
            self.output_console.configure(state="disabled")

    def _on_submit_ai(self):
        editor = self._get_current_editor()
        if editor:
            prompt = self.prompt_entry.get()
            mode = self.mode_selection.get()
            code = editor.get("1.0", "end-1c")

            self.submit_button.configure(state="disabled", text="Getting assistance...")
            
            try:
                if mode == "Generator":
                    generated_code = self.ai_service.get_code_generation(prompt, code)
                    editor.insert("end", "\n\n" + generated_code)
                elif mode == "Mentor":
                    mentor_response = self.ai_service.get_socratic_guidance(prompt, code)
                    self.mentor_output.configure(state="normal")
                    self.mentor_output.delete("1.0", "end")
                    self.mentor_output.insert("1.0", mentor_response)
                    self.mentor_output.configure(state="disabled")
            except Exception as e:
                self.mentor_output.configure(state="normal")
                self.mentor_output.delete("1.0", "end")
                self.mentor_output.insert("1.0", f"An error occurred: {e}")
                self.mentor_output.configure(state="disabled")
            finally:
                self.submit_button.configure(state="normal", text="Get AI Assistance")
