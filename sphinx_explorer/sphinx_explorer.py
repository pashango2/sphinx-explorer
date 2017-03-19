#! coding:utf-8
"""

:StyleSheet:
    https://github.com/ColinDuquesnoy/QDarkStyleSheet
"""
from PySide.QtGui import *
import sys
import os
import qdarkstyle
from .main_window import MainWindow

HOME_DIR = os.path.join(os.path.expanduser('~'), ".sphinx_explorer")


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarkstyle.load_stylesheet())

    main_window = MainWindow(HOME_DIR)
    main_window.show()

    app.exec_()
