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
from PySide.QtGui import *

try:
    app = QApplication(sys.argv)
except RuntimeError:
    pass


here = os.path.dirname(__file__)


def test_table_model():
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
    root_item = model.get("categoryA")

    assert 3 == model.rowCount(root_item.index())
    assert 2 == model.columnCount(root_item.index())

    model.get("categoryA.a").set_value("100")

    obj = model.dump()
    assert {'categoryA': {'a': '100'}, 'categoryB': {}} == obj

    model.clear()
    model.load_settings(setting_obj, default_values=obj)

    item = model.get("categoryA.a")
    assert item.value == "100"


def test_load_settings2():
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

    model.load_settings(yaml.load(settings))
    assert model.rowCount() == 2

    model.clear()
    settings = """
- a
- b
- c
    """.strip()

    model.load_settings(yaml.load(settings))
    assert model.rowCount() == 3

    model.clear()
    settings = """
- "# cat"
- a
- b
    """.strip()

    model.load_settings(yaml.load(settings))
    assert model.rowCount() == 3

    model.clear()
    settings = """
- a:
    - default_value: default
      link: b
- b:
    - value: value
- c
        """.strip()

    print(yaml.load(settings))
    model.load_settings(yaml.load(settings))
    assert model.rowCount() == 3


def test_get_property():
    model = PropertyModel()
    settings = """
- "# categoryA"
-
    - a
- "# categoryB"
-
    - b
- c
    """.strip()

    model.load_settings(yaml.load(settings))

    item = model.get("c")
    assert item.text() == "c"

    item = model.get(("categoryA", "a"))
    assert item.text() == "a"
    assert item.tree_key() == ("categoryA", "a")


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
            "a": [{
                "label": "Document",
            }],
        },
        {
            "b": [{
                "label": "Check",
                "value_type": "TypeBool",
                "default": False
            }]
        },
    ]
    widget.load_settings(settings)

    assert ['Document', 'Check'] == [x.text() for x in widget.properties()]
    check_item = widget.property_map()["b"]  # type: PropertyItem
    assert TypeBool is check_item.value_type
    assert not check_item.value


def test_link():
    widget = PropertyWidget()
    settings = [
        "#category",
        {
            "a": [
                {
                    "label": "Document",
                    "default": "test",
                },
            ]
        },
        {
            "b": [
                {
                    "label": "Document",
                    "link": "a",
                }
            ]
        },
    ]
    widget.load_settings(settings)

    prop_map = widget.property_map()
    item_a = prop_map["a"]
    item_b = prop_map["b"]
    assert item_b.value == "test"

    item_a.set_value("test x")
    assert item_b.value == "test x"
    item_b.set_value("test xx")
    assert item_b.value == "test xx"


# def test_link_and_default():
#     widget = PropertyWidget()
#     default_values = {
#         "a": "sphinx"
#     }
#
#     settings = [
#         "#category",
#         {
#             "a": [{
#                 "label": "Document",
#                 "default": "test",
#             }]
#         },
#         {
#             "b": [{
#                 "label": "Document",
#                 "link": "a",
#             }]
#         },
#     ]
#     # widget.set_default_dict(default_values)
#     widget.load_settings(settings)
#
#     prop_map = widget.property_map()
#     item_a = prop_map["a"]
#     item_b = prop_map["b"]
#     assert item_a.value == "sphinx"
#     assert item_b.value == "sphinx"


def test_required():
    widget = PropertyWidget()

    settings = [
        "#category",
        {
            "a": [{
                "label": "Document",
                "required": True,
            }]
        },
    ]
    widget.load_settings(settings)
    assert False is widget.is_complete()

    widget.property_map()["a"].set_value("test")
    assert True is widget.is_complete()

    # widget.clear()
    # settings = [
    #     "#category",
    #     {
    #         "a": [{
    #             "label": "Document",
    #             "required": True,
    #             "default": "test"
    #         }]
    #     },
    # ]
    # widget.load_settings(settings)
    # assert True is widget.is_complete()
    #
    # default_values = {
    #     "a": "sphinx"
    # }
    # widget.clear()
    # settings = [
    #     "#category",
    #     {
    #         "a": [{
    #             "label": "Document",
    #             "required": True,
    #         }]
    #     },
    # ]
    # widget.set_default_dict(default_values)
    # widget.load_settings(settings)
    # assert True is widget.is_complete()


def test_link_format():
    link = "{_default}/{path}"
    assert ['_default', 'path'] == PropertyItem.parse_link(link)


def test_wizard():
    wizard_path = os.path.join(here, "..", "plugin", "wizard")
    assert os.path.exists(wizard_path)

    params_path = os.path.join(here, "..", "settings")
    assert os.path.exists(params_path)

    quickstart = os.path.join(wizard_path, "quickstart.yml")
    settings = yaml.load(open(quickstart))
    params_dict = toml.load(os.path.join(params_path, "params.toml"))

    model = PropertyModel()
    model.load_settings(
        settings["wizard"],
        params_dict=params_dict,
        default_values={
            "sep": True,
            "path": r"c:\test",
            "project": "test",
        }
    )

    item = model.get("Options.sep")
    assert item and item.value is True

    item = model.get("Required params.path")
    assert item and item.value == r"c:\test\test"

    item.update_link()
    assert item and item.value == r"c:\test\test"

    model.get("Required params.project").set_value("test2")
    assert item and item.value == r"c:\test\test2"





# def test_link_format():
#     widget = PropertyWidget()
#
#     settings = [
#         "#category",
#         {
#             "a": [{
#                 "label": "Document",
#                 "default": "test_a",
#             }]
#         },
#         {
#             "b": [{
#                 "label": "Document",
#                 "link": "a",
#                 "default": "test_b",
#                 "link_format": "{_link_value}/{_default_value}"
#             }]
#         },
#     ]
#     widget.load_settings(settings)
#
#     prop_map = widget.property_map()
#     item_a = prop_map["a"]
#     item_b = prop_map["b"]
#     assert item_a.value == "test_a"
#     assert item_b.value == "test_a/test_b"
#
#     default_values = {
#         "a": "sphinx"
#     }
#     widget.set_default_dict(default_values)
#     assert item_b.value == "sphinx/test_b"


# def test_property_filter():
#     model = PropertyModel()
#
#     settings = [
#         "#category",
#         "a",
#         "b",
#         "#category2",
#         "c",
#     ]
#
#     model.load_settings(settings)
#     assert model.rowCount() == 5
#
#     filter_model = model.create_filter_model(
#         [
#             "a", "b"
#         ]
#     )
#
#     assert filter_model.rowCount() == 2





if __name__ == "__main__":
    import pytest

    pytest.main()
