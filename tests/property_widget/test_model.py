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
from qtpy.QtCore import *
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


def test_allow_empty():
    settings = """
    - a:
        value: ""
        allow_empty: no
        default: "default"
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))
    assert model.a.value == "default"
    model.a.set_value("input")
    assert model.a.value == "input"
    model.a.set_value("")
    assert model.a.value == "default"


def test_check_tree():
    settings = """
    - "#group":
        checkable: yes
        default: yes
    -
        - a
        - b
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))

    assert model.group.a.isEnabled() is True

    model.setData(model.group.index(), Qt.Unchecked, Qt.CheckStateRole)
    assert model.group.a.isEnabled() is False


def test_dump():
    settings = """
    - "#* Epub Settings"
    -
        - epub_cover
        - epub_writing_mode:
            default: horizontal
        - epub_header
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))
    dump = model.dump()
    assert dump == {'Epub Settings': {'epub_writing_mode': 'horizontal'}}

    model.get("Epub Settings").epub_cover.set_value("cover")
    dump = model.dump()
    assert dump == {
        "Epub Settings": {
            "epub_cover": "cover",
            "epub_writing_mode": "horizontal",
        }
    }

    model.clear()
    model.load_settings(yaml.load(settings))
    model.set_values(
        {"Epub Settings": {"epub_cover": "cover"}}
    )
    assert model.get("Epub Settings").epub_cover.value == "cover"

    flat_dump = model.dump(flat=True)
    assert flat_dump == {
        "epub_cover": "cover",
        "epub_writing_mode": "horizontal",
    }

    flat_dump = model.dump(flat=True, exclude_default=True)
    assert flat_dump == {
        "epub_cover": "cover",
    }

    flat_dump = model.dump(flat=True, store_none=True, exclude_default=True)
    assert flat_dump == {
        "epub_cover": "cover",
        "epub_header": None,
    }


def test_type():
    settings = """
    - a:
        value_type: TypeBool
        default: true
    """
    model = PropertyModel()
    model.load_settings(yaml.load(settings))

    assert model.a.value is True


if __name__ == "__main__":
    import pytest

    pytest.main()
