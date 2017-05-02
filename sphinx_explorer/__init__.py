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

sys.path.append("./py35/Scripts")
sys.path.append("./py35/lib/site-packages")
# os.environ.setdefault("QT_API", 'pyside')
# from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import qtpy

import qdarkstyle
from .main_window import MainWindow
import logging
from .about import __version__
# noinspection PyUnresolvedReferences
import mdx_gfm

HOME_DIR = os.path.join(os.path.expanduser('~'), ".sphinx-explorer")


def main():
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
        app.setStyleSheet(qdarkstyle.load_stylesheet(not qtpy.PYQT4))

    translator = QTranslator()
    # noinspection PyArgumentList
    translator.load("i18n/sphinx_explorer_{}".format(QLocale.system().name()))
    app.installTranslator(translator)

    # note: failed
    # setup(app)

    sys_dir = os.path.dirname(sys.argv[0])
    window = MainWindow(sys_dir, HOME_DIR)
    window.show()

    sys.exit(app.exec_())
