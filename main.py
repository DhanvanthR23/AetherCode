import sys
import qdarktheme
from PyQt6.QtWidgets import QApplication
from qt_ui.qt_app_window import AppWindow

def main():
    app = QApplication(sys.argv)
    stylesheet = qdarktheme.load_stylesheet()
    app.setStyleSheet(stylesheet)
    
    window = AppWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
