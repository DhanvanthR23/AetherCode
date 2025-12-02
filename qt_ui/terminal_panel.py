from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtCore import QProcess, QDir, Qt
from PyQt6.QtGui import QTextCursor
import os

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
        self._previous_dir = None

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
        self.process.finished.connect(self.on_process_finished)
        self.process.stateChanged.connect(self.on_process_state_changed)

        self.show_prompt()

    def run_command(self):
        command = self.command_input.text().strip()
        if not command:
            self.show_prompt()
            return

        self.history.append(command)
        self.command_input.history = self.history
        self.command_input.history_index = len(self.history)
        self.output_console.append(self.get_prompt() + command)

        if command == 'clear':
            self.output_console.clear()
            self.show_prompt()
        elif command.startswith("cd "):
            self.handle_cd_command(command)
        elif command == 'cd':
            self.handle_cd_command('cd ~')
        else:
            self.process.start("bash", ["-c", command])

        self.command_input.clear()

    def handle_cd_command(self, command):
        new_dir_str = command[3:].strip()
        current_dir = self.process.workingDirectory()
        
        if new_dir_str == '~':
            new_dir_str = QDir.homePath()
        elif new_dir_str == '-':
            if self._previous_dir:
                new_dir_str = self._previous_dir
            else:
                self.output_console.append("bash: cd: OLDPWD not set")
                self.show_prompt()
                return

        qdir = QDir(current_dir)
        if qdir.cd(new_dir_str):
            self._previous_dir = current_dir
            self.process.setWorkingDirectory(qdir.path())
        else:
            self.output_console.append(f"bash: cd: {new_dir_str}: No such file or directory")
        
        self.show_prompt()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.output_console.insertPlainText(data.data().decode())
        self.output_console.moveCursor(QTextCursor.MoveOperation.End)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.output_console.insertPlainText(data.data().decode())
        self.output_console.moveCursor(QTextCursor.MoveOperation.End)

    def get_prompt(self):
        return f"[{os.path.basename(self.process.workingDirectory())}]$ "

    def show_prompt(self):
        self.output_console.moveCursor(QTextCursor.MoveOperation.End)
        self.output_console.insertPlainText(f"\n{self.get_prompt()}")
        self.output_console.moveCursor(QTextCursor.MoveOperation.End)
        self.command_input.setEnabled(True)
        self.command_input.setFocus()

    def on_process_finished(self):
        self.show_prompt()

    def on_process_state_changed(self, state):
        if state == QProcess.ProcessState.Starting or state == QProcess.ProcessState.Running:
            self.command_input.setEnabled(False)
        else:
            self.command_input.setEnabled(True)
