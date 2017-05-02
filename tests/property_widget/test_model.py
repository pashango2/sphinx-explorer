#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer.property_widget import PropertyWidget, \
    PropertyItem, \
    TypeBool, \
    PropertyModel

import os
import sys
import yaml
import toml
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from .di import *

import platform

try:
    app = QApplication(sys.argv)
except RuntimeError:
    pass


here = os.path.dirname(__file__)


def test_link():
    settings = """
- a
- b:
    link: a
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))
    model.a.set_value("test")
    assert model.a.value == "test"
    assert model.b.value == "test"


def test_link_format():
    settings = """
- a
- b
- c:
    link: ({a}, {b})
- d:
    link: "{_default}: {c}"
    default: def
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))
    model.a.set_value("a")
    model.b.set_value("b")
    assert model.c.value == "(a, b)"
    assert model.d.value == "def: (a, b)"


def test_type():
    settings = """
    - a:
        value_type: TypeBool
        default: true
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))

    assert model.a is True



if __name__ == "__main__":
    import pytest

    pytest.main()
