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
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import sys
import os
import qdarkstyle
from .main_window import MainWindow
import logging

HOME_DIR = os.path.join(os.path.expanduser('~'), ".sphinx-explorer")

__version__ = 0.9


def main():
    # if sys.stdout.encoding is None:
    #     sys.stdout = codecs.open("sphinx-exploere.log", "w", "utf-8")
    # if sys.stderr.encoding is None:
    #     sys.stderr = codecs.open("sphinx-exploere_error.log", "w", "utf-8")
    logging.basicConfig()

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    translator = QTranslator()
    # noinspection PyArgumentList
    translator.load("i18n/sphinx_explorer_{}".format(QLocale.system().name()))
    app.installTranslator(translator)

    sys_dir = os.path.dirname(sys.argv[0])
    window = MainWindow(sys_dir, HOME_DIR)
    window.show()

    sys.exit(app.exec_())
