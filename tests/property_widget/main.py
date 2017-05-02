#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
import sys
import yaml
from tests.property_widget.di import pytest_funcarg__params_dict
from sphinx_explorer.property_widget.frames.tree_dialog_frame import TreeDialog

app = QApplication(sys.argv)

SYSTEM_SETTINGS = """
- "#*Editor":
    - label: Editor
- "#*Default Values":
    - label: Default Values
-
    - path
    - author
    - language
    - html_theme
    - sep

- "#*Python Interpreter"
-
    - python
- "#*Extensions":
    - label: Extensions
-
    - "#*test"
"""

settings = yaml.load(SYSTEM_SETTINGS)
params_dict = pytest_funcarg__params_dict(None)

dialog = TreeDialog()
dialog.property_model.load_settings(settings, params_dict)
dialog.show()
app.exec_()