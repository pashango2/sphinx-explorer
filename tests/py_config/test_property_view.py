#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.py_config import ConfigModel, PropertyView
import sys
from qtpy.QtWidgets import *
from qtpy.QtCore import *


# def test_load():
#     yaml_string = """
# - zSetting:
#     type: 'integer'
#     default: 4
# - aSetting:
#     type: 'integer'
#     default: 4
#     """.strip()
#
#     app = QApplication(sys.argv)
#     view = PropertyView()
#
#     config = ConfigModel.from_yaml_string(yaml_string)
#     view.setModel(config)
#
#     yaml_string = """
# - someSetting:
#      type: 'integer'
#      default: 4
#      enum: [2, 4, 6, 8]
#     """.strip()
#
#     config = ConfigModel.from_yaml_string(yaml_string)
#     view.setModel(config)
#     # view.show()
#     # app.exec_()
#
#     yaml_string = """
# - someSetting:
#     type: 'string'
#     default: 'foo'
#     enum: [
#       {value: 'foo', description: 'Foo mode. You want this.'},
#       {value: 'bar', description: 'Bar mode. Nobody wants that!'}
#     ]
#     """.strip()
#
#     config = ConfigModel.from_yaml_string(yaml_string)
#     view.setModel(config)
#
#     yaml_string = """
# - "#Category"
# -
#     - a:
#         type: string
#         default: "a"
#     - b:
#         type: string
#         default: "b"
# - c:
#     type: string
#     """.strip()
#
#
# def test_load2():
#     yaml_string = """
# - "#Category"
# -
#     - a:
#         type: string
#         default: "a"
#     - b:
#         type: boolean
#         default: true
#     - "#SubCategory"
#     -
#         - c:
#             type: string
# - d:
#     type: string
#     """.strip()
#     app = QApplication(sys.argv)
#     view = PropertyView()
#
#     print(view.__dict__)
#     print(view.addAction)
#     print(QTableView.__dict__)
#
#     config = ConfigModel.from_yaml_string(yaml_string)
#     # view.setModel(config)
#     # view.show()
#     # app.exec_()
