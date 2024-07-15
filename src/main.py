import sys

from PySide6.QtWidgets import QApplication
import PySide6.QtAsyncio as QtAsyncio

from view import MainWindow


def main():
    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    # app.exec()
    QtAsyncio.run()