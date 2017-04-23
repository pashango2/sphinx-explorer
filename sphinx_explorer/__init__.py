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
import os
import sys
# os.environ.setdefault("QT_API", 'pyside')
# from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import qtpy

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
    if qtpy.PYQT5:
        style_sheet = qdarkstyle.load_stylesheet_pyqt5()
        # add patch
        style_sheet += """
QLineEdit
{
    padding: 0px;
}
        """

        app.setStyleSheet(style_sheet)
    else:
        pyside = not qtpy.PYQT4
        app.setStyleSheet(qdarkstyle.load_stylesheet(pyside))

    translator = QTranslator()
    # noinspection PyArgumentList
    translator.load("i18n/sphinx_explorer_{}".format(QLocale.system().name()))
    app.installTranslator(translator)

    sys_dir = os.path.dirname(sys.argv[0])
    window = MainWindow(sys_dir, HOME_DIR)
    window.show()

    sys.exit(app.exec_())
