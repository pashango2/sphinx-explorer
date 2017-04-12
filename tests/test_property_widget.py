#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer.property_widget import PropertyWidget, PropertyItem, TypeBool
import sys
import os
from PySide.QtGui import *

try:
    app = QApplication(sys.argv)
except RuntimeError:
    pass


def test_load_settings():
    widget = PropertyWidget()

    # category and basic param
    settings = [
        "#category",
        "a",
        "b",
        "c",
    ]

    widget.load_settings(settings)
    assert [u'a', u'b', u'c'] == [x.text() for x in widget.properties()]
    widget.clear()

    # Detailed parameters
    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
        },
        {
            "key": "b",
            "label": "Check",
            "value_type": "TypeBool",
            "default": False
        },
    ]
    widget.load_settings(settings)

    assert ['Document', 'Check'] == [x.text() for x in widget.properties()]
    check_item = widget.property_map()["b"]     # type: PropertyItem
    assert TypeBool is check_item.value_type
    assert False is check_item.value


def test_link():
    widget = PropertyWidget()
    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
            "default": "test",
        },
        {
            "key": "b",
            "label": "Document",
            "link": "a",
        },
    ]
    widget.load_settings(settings)

    prop_map = widget.property_map()
    item_a = prop_map["a"]
    item_b = prop_map["b"]
    assert item_b.link.key == "a"
    assert item_b.value == "test"

    item_a.set_value("test x")
    assert item_b.value == "test x"
    item_b.set_value("test xx")
    assert item_b.value == "test xx"


def test_link_and_default():
    widget = PropertyWidget()
    default_values = {
        "a": "sphinx"
    }

    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
            "default": "test",
        },
        {
            "key": "b",
            "label": "Document",
            "link": "a",
        },
    ]
    widget.set_default_dict(default_values)
    widget.load_settings(settings, default_values)

    prop_map = widget.property_map()
    item_a = prop_map["a"]
    item_b = prop_map["b"]
    assert item_b.link.key == "a"
    assert item_a.value == "sphinx"
    assert item_b.value == "sphinx"


def test_required():
    widget = PropertyWidget()

    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
            "required": True,
        },
    ]
    widget.load_settings(settings)
    assert False is widget.is_complete()

    widget.property_map()["a"].set_value("test")
    assert True is widget.is_complete()

    widget.clear()
    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
            "required": True,
            "default": "test"
        },
    ]
    widget.load_settings(settings)
    assert True is widget.is_complete()

    default_values = {
        "a": "sphinx"
    }
    widget.clear()
    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
            "required": True,
        },
    ]
    widget.set_default_dict(default_values)
    widget.load_settings(settings)
    assert True is widget.is_complete()


def test_link_format():
    widget = PropertyWidget()

    settings = [
        "#category",
        {
            "key": "a",
            "label": "Document",
            "default": "test",
        },
        {
            "key": "b",
            "label": "Document",
            "link": "a",
            "default": "test",
            "link_format": "{_default}{_path_sep}{_link}",
        },
    ]
    widget.load_settings(settings)

    prop_map = widget.property_map()
    item_a = prop_map["a"]
    item_b = prop_map["b"]
    assert item_a.value == "test"
    assert item_b.value == os.path.join("test", "test")

    default_values = {
        "a": "sphinx"
    }
    widget.set_default_dict(default_values)


def test_add_item():
    widget = PropertyWidget()
    widget.add_property(
        "name",
        {
            "value": "test"
        }
    )

    obj = widget.dump()
    assert obj == {"name": "test"}


if __name__ == "__main__":
    import pytest
    pytest.main()
