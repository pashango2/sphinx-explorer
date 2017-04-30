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


def pytest_funcarg__simple_model(request):
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

    return model


def test_property_widget(simple_model):
    widget = PropertyWidget()
    widget.setModel(simple_model)
    # widget.show()

    assert simple_model.rowCount() > 0

    index = widget.first_property_index()
    assert index.isValid()
    print(index.data())
    # QTest.mouseClick(widget, Qt.LeftButton)



    pass