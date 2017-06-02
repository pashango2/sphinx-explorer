#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.py_config import ConfigModel, FormLayoutPage
import sys
from string import Formatter
from qtpy.QtWidgets import *
from qtpy.QtCore import *

from sphinx_explorer.py_config.py_config import Map, parse_default_format


def test_load():
    yaml_string = """
- zSetting:
    type: 'integer'
    default: 4
- aSetting:
    type: 'integer'
    default: 4
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    assert config.get("zSetting") == 4
    assert config.get("aSetting") == 4
    assert ("zSetting", "aSetting") == tuple(key.text() for _, key in config.config_iter())

    yaml_string = """
- someSetting:
    type: 'integer'
    default: 4
    enum: [2, 4, 6, 8]
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    assert config.get("someSetting") == 4

    config.set("someSetting", 6)
    assert config.get("someSetting") == 6

    yaml_string = """
- someSetting:
    type: 'string'
    default: 'foo'
    enum: [
      {value: 'foo', description: 'Foo mode. You want this.'},
      {value: 'bar', description: 'Bar mode. Nobody wants that!'}
    ]
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    assert config.get("someSetting") == "foo"
    try:
        config.set("someSetting", "s")
    except ValueError:
        pass
    else:
        assert False

    config.set("someSetting", "bar")
    assert config.get("someSetting") == "bar"


def test_dump():
    yaml_string = """
- "#Category"
-
    - a:
        type: string
        default: "a"
    - b:
        type: string
        default: "b"
    - c:
        type: string
    - "#SubCategory"
    -
        - non:
            type: string
- d:
    type: string
    default: d
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    value = config.dump(enable_default_value=True)
    assert {'d': 'd', 'Category': {'b': 'b', 'a': 'a'}} == value

    category_item = config.get_item("Category")
    value = config.dump(category_item.index(), enable_default_value=True)
    assert {'b': 'b', 'a': 'a'} == value

    assert {} == config.dump()
    config.set("Category.a", "a!")
    assert {'Category': {'a': 'a!'}} == config.dump()


def test_default_value():
    yaml_string = """
- a:
    type: string
- b:
    type: string
    default: b
- c:
    type: string
    default: c
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)
    value = config.dump()
    assert {} == value

    values_dict = {
        "a": "a!",
        "b": "b!",
    }
    config = ConfigModel.from_yaml_string(yaml_string, values_dict)
    value = config.dump()
    assert {'a': 'a!', 'b': 'b!'} == value


def test_link():
    yaml_string = """
- "#A"
-
    - a:
        type: string
        default: "a"
- "#B"
-
    - b:
        type: string
        default: "{A.a}"
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    assert config.get("A.a") == "a"
    assert config.get("B.b") == "a"

    config.get_item("A.a").set_value("c")
    assert config.get("A.a") == "c"
    assert config.get("B.b") == "c"

    config.get_item("B.b").set_value("d")
    config.get_item("A.a").set_value("e")
    assert config.get("A.a") == "e"
    assert config.get("B.b") == "d"


class MapDict(dict):
    def __init__(self, initial_dict):
        super(MapDict, self).__init__()
        self._d = initial_dict

    def __missing__(self, key):

        return self._d[key]


def test_link_format():
    yaml_string = """
- "#A"
-
    - a:
        type: string
        default: "a"
    - aa:
        type: string
        default: "{a}"
- "#B"
-
    - b:
        type: string
        default: "{A.a}"
        """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    assert config.get("A.a") == "a"
    assert config.get("B.b") == "a"

    config.get_item("A.a").set_value("c")
    assert config.get("A.a") == "c"
    assert config.get("B.b") == "c"

    config.get_item("B.b").set_value("d")
    config.get_item("A.a").set_value("e")
    assert config.get("A.a") == "e"
    assert config.get("B.b") == "d"


def test_form_layout():
    # app = QApplication(sys.argv)

    yaml_string = """
- foo_bar:
    type: string
    default: foo
    enum: [
      {value: 'foo', description: 'Foo mode. You want this.'},
      {value: 'bar', description: 'Bar mode. Nobody wants that!'}
    ]
- bool_setting:
    type: boolean
    default: true
    """.strip()

    config = ConfigModel.from_yaml_string(yaml_string)

    # page = FormLayoutPage(config, None)
    # layout = page.setup()
    # page.commit()

    # dlg = QDialog()
    # dlg.setLayout(layout)
    # dlg.exec_()
    #
    # app.exec_()


