from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class FindReplacePanel(QWidget):
    # Define signals
    find_next_requested = pyqtSignal(str, dict)
    find_in_project_requested = pyqtSignal(str, dict)
    replace_requested = pyqtSignal(str, str, dict)
    replace_all_requested = pyqtSignal(str, str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FindReplacePanel")

        layout = QVBoxLayout()
        self.setLayout(layout)

        find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        layout.addWidget(find_label)
        layout.addWidget(self.find_input)

        replace_label = QLabel("Replace:")
        self.replace_input = QLineEdit()
        layout.addWidget(replace_label)
        layout.addWidget(self.replace_input)

        options_layout = QHBoxLayout()
        self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        self.whole_words_checkbox = QCheckBox("Whole Words")
        self.regex_checkbox = QCheckBox("Regex")
        options_layout.addWidget(self.case_sensitive_checkbox)
        options_layout.addWidget(self.whole_words_checkbox)
        options_layout.addWidget(self.regex_checkbox)
        layout.addLayout(options_layout)

        self.find_next_button = QPushButton("Find Next")
        layout.addWidget(self.find_next_button)

        self.find_in_project_button = QPushButton("Find in Project")
        layout.addWidget(self.find_in_project_button)

        self.replace_button = QPushButton("Replace")
        layout.addWidget(self.replace_button)

        self.replace_all_button = QPushButton("Replace All")
        layout.addWidget(self.replace_all_button)

        layout.addStretch()

        # Connect buttons to emit signals
        self.find_next_button.clicked.connect(self._emit_find_next)
        self.find_in_project_button.clicked.connect(self._emit_find_in_project)
        self.replace_button.clicked.connect(self._emit_replace)
        self.replace_all_button.clicked.connect(self._emit_replace_all)

    def _get_options(self):
        return {
            "case_sensitive": self.case_sensitive_checkbox.isChecked(),
            "whole_words": self.whole_words_checkbox.isChecked(),
            "regex": self.regex_checkbox.isChecked(),
        }

    def _emit_find_next(self):
        self.find_next_requested.emit(self.find_input.text(), self._get_options())

    def _emit_find_in_project(self):
        self.find_in_project_requested.emit(self.find_input.text(), self._get_options())

    def _emit_replace(self):
        self.replace_requested.emit(self.find_input.text(), self.replace_input.text(), self._get_options())

    def _emit_replace_all(self):
        self.replace_all_requested.emit(self.find_input.text(), self.replace_input.text(), self._get_options())
