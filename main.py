import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ui.window.main_window import MainWindow


APP_VERSION = "3.0.0"


def main() -> None:
    # Avoid platform-dependent font/widget surprises during startup.
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Chromium Theme Studio")
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Chromium Theme Studio")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
