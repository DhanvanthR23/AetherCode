import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream
from qt_ui.qt_app_window import AppWindow

def main():
    app = QApplication(sys.argv)

    # Load the stylesheet
    style_file = QFile("qt_ui/themes/dracula.qss")
    style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
    stylesheet = QTextStream(style_file).readAll()
    app.setStyleSheet(stylesheet)

    window = AppWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
