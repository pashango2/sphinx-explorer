#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
from sphinx_explorer import python_venv
from qtpy.QtTest import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *
import yaml
from sphinx_explorer.property_widget import PropertyWidget, PropertyModel

app = QApplication(sys.argv)


def pytest_funcarg__mysetup(request):
    model = PropertyModel()
    settings = """
- "# categoryA"
-
    - a
    - b
    - c
- "# categoryB"
-
    - d
    - e
    - f
    """.strip()

    setting_obj = yaml.load(settings)
    model.load_settings(setting_obj)


def test_property_widget():
    widget = PropertyWidget()
    widget.show()

    app.exec_()

    QTest.mouseClick(widget, Qt.LeftButton)



test_property_widget()