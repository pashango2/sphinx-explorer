#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
"""

:StyleSheet:
    https://github.com/ColinDuquesnoy/QDarkStyleSheet

:dependent:
    * toml
    * qdarkstyle
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

    window = MainWindow(HOME_DIR)
    window.show()

    app.exec_()
