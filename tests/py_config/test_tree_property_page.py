#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.py_config import ConfigModel
import sys
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtTest import *


def test_page():
    yaml_string = """
- "# epub":
    label: epub setting
-
    - "## epub setting"
    - type:
        type: string
        enum: [ vertical, horizontal ]
- "# pdf"
-
    - paper_type:
        type: string
        enum: [ A4, A5, B4, B5 ]
    """.strip()

    # app = QApplication(sys.argv)
    config = ConfigModel.from_yaml_string(yaml_string)

    tree_model = config.create_category_tree_proxy_model(None)

    assert tree_model.rowCount() == 2

    first_index = tree_model.index(0, 0)
    assert tree_model.rowCount(first_index) == 0

    item = config.get_item("epub.type")
    assert item is not None

    # view = QTreeView()
    # view.setModel(tree_model)
    # view.show()
    # app.exec_()
