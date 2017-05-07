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

from qtpy.QtCore import *
from qtpy.QtWidgets import *
import qtpy

import qdarkstyle
from .main_window import MainWindow
import logging
from .about import __version__
# noinspection PyUnresolvedReferences
import mdx_gfm
from .util import icon

HOME_DIR = os.path.join(os.path.expanduser('~'), ".sphinx-explorer")


def main(sys_dir=None):
    logging.basicConfig()

    icon.init(sys_dir)

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
    i18n_path = os.path.join(sys_dir, "settings/i18n/sphinx_explorer_{}".format(QLocale.system().name()))
    translator.load(i18n_path)
    app.installTranslator(translator)

    window = MainWindow(sys_dir, HOME_DIR)
    window.show()

    sys.exit(app.exec_())


def package_main():
    main(os.path.dirname(__file__))


def exec_main():
    main(os.path.dirname(sys.argv[0]))
