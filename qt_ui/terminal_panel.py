from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtCore import QProcess, QDir, Qt
from PyQt6.QtGui import QTextCursor

class CommandInput(QLineEdit):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.history = history
        self.history_index = len(self.history)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.setText(self.history[self.history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index < len(self.history):
                self.history_index += 1
                if self.history_index < len(self.history):
                    self.setText(self.history[self.history_index])
                else:
                    self.clear()
        else:
            super().keyPressEvent(event)

class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TerminalPanel")

        self.history = []

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

        self.command_input = CommandInput(self.history)
        self.command_input.returnPressed.connect(self.run_command)
        layout.addWidget(self.command_input)

        self.process = QProcess(self)
        self.process.setWorkingDirectory(QDir.currentPath())
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.show_prompt)

        self.show_prompt()

    def run_command(self):
        command = self.command_input.text()
        if command:
            self.history.append(command)
            self.command_input.history = self.history
            self.command_input.history_index = len(self.history)
            
            self.output_console.append(self.get_prompt() + command)
            if command.startswith("cd "):
                # Handle 'cd' command separately
                dir = command[3:].strip()
                if self.process.workingDirectory():
                    new_dir = QDir(self.process.workingDirectory())
                    if new_dir.cd(dir):
                        self.process.setWorkingDirectory(new_dir.path())
                self.show_prompt()
            else:
                self.process.start("bash", ["-c", command])
            self.command_input.clear()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.output_console.insertPlainText(data.data().decode())

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.output_console.insertPlainText(data.data().decode())
    
    def get_prompt(self):
        return f"[{self.process.workingDirectory()}]$ "

    def show_prompt(self):
        self.output_console.moveCursor(QTextCursor.MoveOperation.End)
        self.output_console.insertPlainText(f"\n{self.get_prompt()}")
        self.output_console.moveCursor(QTextCursor.MoveOperation.End)
