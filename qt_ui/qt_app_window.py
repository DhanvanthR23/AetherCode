from PyQt6.QtWidgets import (QMainWindow, QDockWidget, QTreeView, QTabWidget, 
                             QVBoxLayout, QWidget, QLabel, QTextEdit, QPushButton, 
                             QHBoxLayout, QFileDialog)
from PyQt6.QtGui import QFileSystemModel, QAction
from PyQt6.QtCore import QDir, Qt
from qt_ui.qt_code_editor import CodeEditor
from app.ai_service import AIService
import os

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AetherCode")
        self.resize(1200, 800)

        self.ai_service = AIService()
        self.open_tabs = {}

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        self.create_menu_bar()
        self.create_file_explorer()
        self.create_ai_panel()

        self.show()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

    def create_file_explorer(self):
        file_explorer_dock = QDockWidget("File Explorer", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, file_explorer_dock)

        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(QDir.currentPath())

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setRootIndex(self.fs_model.index(QDir.currentPath()))
        self.tree_view.doubleClicked.connect(self.open_file)

        file_explorer_dock.setWidget(self.tree_view)

    def create_ai_panel(self):
        ai_panel_dock = QDockWidget("AI Panel", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, ai_panel_dock)

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
        ai_panel_dock.setWidget(ai_panel_widget)

    def open_file(self, index):
        path = self.fs_model.filePath(index)
        if os.path.isfile(path):
            self.open_path(path)

    def open_path(self, path):
        editor = CodeEditor()
        with open(path, 'r') as f:
            editor.setText(f.read())
        index = self.tab_widget.addTab(editor, os.path.basename(path))
        self.open_tabs[index] = path

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_name:
            self.open_path(file_name)

    def save_file(self):
        current_index = self.tab_widget.currentIndex()
        if current_index in self.open_tabs:
            path = self.open_tabs[current_index]
            editor = self.tab_widget.widget(current_index)
            with open(path, 'w') as f:
                f.write(editor.text())
        else:
            self.save_file_as()

    def save_file_as(self):
        current_index = self.tab_widget.currentIndex()
        editor = self.tab_widget.widget(current_index)
        if editor:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File As")
            if file_name:
                with open(file_name, 'w') as f:
                    f.write(editor.text())
                self.open_tabs[current_index] = file_name
                self.tab_widget.setTabText(current_index, os.path.basename(file_name))

    def close_tab(self, index):
        if index in self.open_tabs:
            del self.open_tabs[index]
        self.tab_widget.removeTab(index)

    def run_generator_mode(self):
        prompt = self.ai_prompt_input.toPlainText()
        current_editor = self.tab_widget.currentWidget()
        if not isinstance(current_editor, CodeEditor):
            self.ai_output_console.setText("Please open a file to use the AI features.")
            return
        code = current_editor.text()
        generated_code = self.ai_service.get_code_generation(prompt, code)
        self.ai_output_console.setText(generated_code)

    def run_mentor_mode(self):
        prompt = self.ai_prompt_input.toPlainText()
        current_editor = self.tab_widget.currentWidget()
        if not isinstance(current_editor, CodeEditor):
            self.ai_output_console.setText("Please open a file to use the AI features.")
            return
        code = current_editor.text()
        guidance = self.ai_service.get_socratic_guidance(prompt, code)
        self.ai_output_console.setText(guidance)