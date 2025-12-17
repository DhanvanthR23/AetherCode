from PyQt6.QtWidgets import (QMainWindow, QDockWidget, QTreeView, QTabWidget, 
                             QVBoxLayout, QWidget, QLabel, QTextEdit, QPushButton, 
                             QHBoxLayout, QFileDialog)
from PyQt6.QtGui import QFileSystemModel, QAction, QStandardItemModel, QStandardItem
from PyQt6.QtCore import QDir, Qt
from qt_ui.qt_code_editor import CodeEditor
from qt_ui.find_replace_panel import FindReplacePanel
from qt_ui.terminal_panel import TerminalPanel
from app.ai_service import AIService
import os
import subprocess

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AetherCode")
        self.resize(1200, 800)

        self.ai_service = AIService()
        self.ai_service.generation_finished.connect(self.on_generation_finished)
        self.ai_service.guidance_finished.connect(self.on_guidance_finished)
        self.ai_service.error.connect(self.on_ai_error)

        self.open_tabs = {}

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        self.create_menu_bar()
        self.create_file_explorer()
        self.create_ai_panel()
        self.create_find_replace_panel()
        self.create_terminal_panel()

        self.show()

    def on_generation_finished(self, generated_code):
        self.ai_output_console.setText(generated_code)
        self.generator_mode_button.setEnabled(True)
        self.mentor_mode_button.setEnabled(True)

    def on_guidance_finished(self, guidance):
        self.ai_output_console.setText(guidance)
        self.generator_mode_button.setEnabled(True)
        self.mentor_mode_button.setEnabled(True)

    def on_ai_error(self, error_message):
        self.ai_output_console.setText(f"An error occurred: {error_message}")
        self.generator_mode_button.setEnabled(True)
        self.mentor_mode_button.setEnabled(True)


    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        find_replace_action = QAction("Find/Replace", self)
        find_replace_action.triggered.connect(self.toggle_find_replace_panel)
        edit_menu.addAction(find_replace_action)

        terminal_action = QAction("Terminal", self)
        terminal_action.triggered.connect(self.toggle_terminal_panel)
        view_menu.addAction(terminal_action)


    def create_file_explorer(self):
        self.file_explorer_dock = QDockWidget("File Explorer", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_explorer_dock)

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setRootIndex(self.fs_model.index(QDir.currentPath()))
        self.tree_view.doubleClicked.connect(self.open_file)

        self.file_explorer_dock.setWidget(self.tree_view)

    def create_ai_panel(self):
        self.ai_panel_dock = QDockWidget("AI Panel", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_panel_dock)

        ai_panel_widget = QWidget()
        ai_panel_layout = QVBoxLayout()

        self.ai_prompt_input = QTextEdit()
        self.ai_prompt_input.setPlaceholderText("Enter your prompt here...")
        ai_panel_layout.addWidget(self.ai_prompt_input)

        button_layout = QHBoxLayout()
        self.generator_mode_button = QPushButton("Generator Mode")
        self.mentor_mode_button = QPushButton("Mentor Mode")
        button_layout.addWidget(self.generator_mode_button)
        button_layout.addWidget(self.mentor_mode_button)
        ai_panel_layout.addLayout(button_layout)

        self.generator_mode_button.clicked.connect(self.run_generator_mode)
        self.mentor_mode_button.clicked.connect(self.run_mentor_mode)

        self.ai_output_console = QTextEdit()
        self.ai_output_console.setReadOnly(True)
        ai_panel_layout.addWidget(self.ai_output_console)

        ai_panel_widget.setLayout(ai_panel_layout)
        self.ai_panel_dock.setWidget(ai_panel_widget)

    def create_find_replace_panel(self):
        self.find_replace_dock = QDockWidget("Find/Replace", self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.find_replace_dock)

        self.find_replace_panel = FindReplacePanel()
        self.find_replace_dock.setWidget(self.find_replace_panel)
        self.find_replace_dock.hide()

        self.find_replace_panel.find_next_requested.connect(self.find_next)
        self.find_replace_panel.find_in_project_requested.connect(self.find_in_project)
        self.find_replace_panel.replace_requested.connect(self.replace_text)
        self.find_replace_panel.replace_all_requested.connect(self.replace_all_text)

        self.create_search_results_panel()

    def create_search_results_panel(self):
        self.search_results_dock = QDockWidget("Search Results", self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.search_results_dock)

        self.search_results_tree = QTreeView()
        self.search_results_tree.doubleClicked.connect(self.go_to_search_result)
        self.search_results_dock.setWidget(self.search_results_tree)
        self.search_results_dock.hide()

    def create_terminal_panel(self):
        self.terminal_dock = QDockWidget("Terminal", self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        self.terminal_panel = TerminalPanel()
        self.terminal_dock.setWidget(self.terminal_panel)
        self.terminal_dock.hide()

    def toggle_terminal_panel(self):
        if self.terminal_dock.isVisible():
            self.terminal_dock.hide()
        else:
            self.terminal_dock.show()

    def find_in_project(self, search_text, options):
        if not search_text:
            return

        self.search_results_dock.show()
        
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['File', 'Line', 'Content'])
        self.search_results_tree.setModel(model)

        root_path = self.fs_model.rootPath()
        try:
            command = ["rg", "-n", "-H", "--with-filename", "--no-heading", "--line-buffered"]
            if not options.get("case_sensitive"):
                command.append("-i")
            if options.get("whole_words"):
                command.append("-w")
            if not options.get("regex"):
                command.append("-F") # Fixed strings

            command.extend([search_text, root_path])
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in process.stdout:
                parts = line.strip().split(':', 2)
                if len(parts) == 3:
                    filepath, line_number, content = parts
                    file_item = QStandardItem(filepath)
                    line_item = QStandardItem(line_number)
                    content_item = QStandardItem(content)
                    model.appendRow([file_item, line_item, content_item])
            process.wait()
            if process.returncode != 0 and process.returncode != 1:
                stderr_output = process.stderr.read()
                print(f"Error during ripgrep search: {stderr_output}")

        except FileNotFoundError:
            print("ripgrep (rg) not found. Please install it to use project-wide search.")
        except Exception as e:
            print(f"An error occurred during project search: {e}")

    def go_to_search_result(self, index):
        model = self.search_results_tree.model()
        file_path_item = model.item(index.row(), 0)
        line_number_item = model.item(index.row(), 1)
        if file_path_item and line_number_item:
            file_path = file_path_item.text()
            line_number = int(line_number_item.text())
            self.open_path(file_path)
            
            editor = self.tab_widget.currentWidget()
            if isinstance(editor, CodeEditor):
                editor.setCursorPosition(line_number - 1, 0)

    def toggle_find_replace_panel(self):
        if self.find_replace_dock.isVisible():
            self.find_replace_dock.hide()
        else:
            self.find_replace_dock.show()

    def open_file(self, index):
        path = self.fs_model.filePath(index)
        if os.path.isfile(path):
            self.open_path(path)

    def open_path(self, path):
        if path in self.open_tabs:
            editor = self.open_tabs[path]
            self.tab_widget.setCurrentWidget(editor)
            return

        editor = CodeEditor()
        editor.path = path
        try:
            with open(path, 'r') as f:
                editor.setText(f.read())
            self.tab_widget.addTab(editor, os.path.basename(path))
            self.open_tabs[path] = editor
            self.tab_widget.setCurrentWidget(editor)
        except Exception as e:
            print(f"Could not open file {path}: {e}")

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_name:
            self.open_path(file_name)

    def save_file(self):
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, CodeEditor):
            return

        path_to_save = None
        for path, editor_widget in self.open_tabs.items():
            if editor_widget == editor:
                path_to_save = path
                break
        
        if path_to_save:
            with open(path_to_save, 'w') as f:
                f.write(editor.text())
        else:
            self.save_file_as()

    def save_file_as(self):
        editor = self.tab_widget.currentWidget()
        if not isinstance(editor, CodeEditor):
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if file_name:
            # Remove old path if it exists
            old_path = None
            for path, editor_widget in self.open_tabs.items():
                if editor_widget == editor:
                    old_path = path
                    break
            if old_path:
                del self.open_tabs[old_path]

            with open(file_name, 'w') as f:
                f.write(editor.text())
            
            editor.path = file_name
            self.open_tabs[file_name] = editor
            current_index = self.tab_widget.indexOf(editor)
            self.tab_widget.setTabText(current_index, os.path.basename(file_name))

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if not isinstance(widget, CodeEditor):
            self.tab_widget.removeTab(index)
            return

        path_to_close = None
        for path, editor_widget in self.open_tabs.items():
            if editor_widget == widget:
                path_to_close = path
                break
        
        if path_to_close:
            del self.open_tabs[path_to_close]
        
        self.tab_widget.removeTab(index)

    def run_generator_mode(self):
        prompt = self.ai_prompt_input.toPlainText()
        current_editor = self.tab_widget.currentWidget()
        if not isinstance(current_editor, CodeEditor):
            self.ai_output_console.setText("Please open a file to use the AI features.")
            return
        
        self.ai_output_console.setText("Generating code...")
        self.generator_mode_button.setEnabled(False)
        self.mentor_mode_button.setEnabled(False)
        
        code = current_editor.text()
        self.ai_service.get_code_generation(prompt, code)

    def run_mentor_mode(self):
        prompt = self.ai_prompt_input.toPlainText()
        current_editor = self.tab_widget.currentWidget()
        if not isinstance(current_editor, CodeEditor):
            self.ai_output_console.setText("Please open a file to use the AI features.")
            return

        self.ai_output_console.setText("Getting guidance...")
        self.generator_mode_button.setEnabled(False)
        self.mentor_mode_button.setEnabled(False)

        code = current_editor.text()
        self.ai_service.get_socratic_guidance(prompt, code)

    def find_next(self, search_text, options):
        current_editor = self.tab_widget.currentWidget()
        if isinstance(current_editor, CodeEditor):
            current_editor.find_next_in_editor(search_text, options)

    def replace_text(self, search_text, replace_text, options):
        current_editor = self.tab_widget.currentWidget()
        if isinstance(current_editor, CodeEditor):
            current_editor.replace_in_editor(search_text, replace_text, options)

    def replace_all_text(self, search_text, replace_text, options):
        current_editor = self.tab_widget.currentWidget()
        if isinstance(current_editor, CodeEditor):
            current_editor.replace_all_in_editor(search_text, replace_text, options)