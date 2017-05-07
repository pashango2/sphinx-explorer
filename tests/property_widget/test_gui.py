#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import sys
from sphinx_explorer import python_venv
from qtpy.QtTest import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *
import yaml
import toml
from sphinx_explorer.property_widget import PropertyWidget, PropertyModel

from .di import *

app = QApplication(sys.argv)


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