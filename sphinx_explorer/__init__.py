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

HOME_DIR = os.path.join(os.path.expanduser('~'), ".sphinx-explorer")

__version__ = 0.9


def main():
    # if sys.stdout.encoding is None:
    #     sys.stdout = codecs.open("sphinx-exploere.log", "w", "utf-8")
    # if sys.stderr.encoding is None:
    #     sys.stderr = codecs.open("sphinx-exploere_error.log", "w", "utf-8")

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    sys_dir = os.path.dirname(sys.argv[0])
    window = MainWindow(sys_dir, HOME_DIR)
    window.show()

    sys.exit(app.exec_())
