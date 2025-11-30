from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtCore import QProcess

class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TerminalPanel")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.run_command)
        layout.addWidget(self.command_input)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

    def run_command(self):
        command = self.command_input.text()
        if command:
            self.output_console.append(f"$ {command}")
            self.process.start("bash", ["-c", command])
            self.command_input.clear()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.output_console.append(data.data().decode().strip())

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.output_console.append(data.data().decode().strip())
