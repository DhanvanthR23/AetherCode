from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel

class FindReplacePanel(QWidget):
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

        self.find_next_button = QPushButton("Find Next")
        layout.addWidget(self.find_next_button)

        self.find_in_project_button = QPushButton("Find in Project")
        layout.addWidget(self.find_in_project_button)

        self.replace_button = QPushButton("Replace")
        layout.addWidget(self.replace_button)

        self.replace_all_button = QPushButton("Replace All")
        layout.addWidget(self.replace_all_button)

        layout.addStretch()
