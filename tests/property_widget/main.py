#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
import sys
import yaml
from sphinx_explorer.property_widget.frames.tree_dialog_frame import TreeDialog

app = QApplication(sys.argv)

SYSTEM_SETTINGS = """
- "#*Editor":
    label: Editor
    
- "#*Epub"
-
    - "#Enable":
        checkable: yes
    -
        - eput_name
    
- "#*Default Values":
    label: Default Values
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
    label: Extensions
-
    - "#*test"
"""

settings = yaml.load(SYSTEM_SETTINGS)
print(settings)

dialog = TreeDialog()
dialog.property_model.load_settings(settings)
dialog.show()
app.exec_()