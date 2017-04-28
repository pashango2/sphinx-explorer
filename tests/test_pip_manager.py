#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
# import os
# os.environ.setdefault("QT_API", 'pyside')

from sphinx_explorer.util.commander import commander
# from qtpy.QtCore import *
from qtpy.QtWidgets import *
# from PySide.QtCore import *
# from PySide.QtGui import *
from sphinx_explorer import python_venv

# noinspection PyBroadException
try:
    app = QApplication(sys.argv)
except:
    pass


def test_extension():
    task = python_venv.PipListTask(commander=commander)
    task.run()
    assert task.packages

    model = python_venv.PackageModel()
    model.load(task.packages)

    out_task = python_venv.PipListOutDateTask(commander=commander)
    out_task.run()
    assert task.packages

    print(model.rowCount())
    assert 1 < model.rowCount()


def test_parse():
    output = """
Package             Version   Latest      Type
------------------- --------- ----------- -----
astroid             1.4.9     1.5.2       wheel
binaryornot         0.4.0     0.4.3       wheel
    """.strip()

    packages = list(python_venv.PipListOutDateTask.outdate_filter(output))

    assert packages[0] == (u'astroid', u'1.4.9', u'1.5.2', u'wheel')
    assert packages[1] == (u'binaryornot', u'0.4.0', u'0.4.3', u'wheel')


def test_filter():
    output = """
actdiag (0.5.4)
alabaster (0.7.10)
apng (0.1.0)
appdirs (1.4.3)
argh (0.26.2)
    """.strip()

    packages = list(python_venv.PipListOutDateTask.filter(output))

    model = python_venv.PackageModel()
    model.load(packages)

    assert model.rowCount() == 5

    filter_packages = ["actdiag", "apng"]
    filter_model = model.create_filter_model(filter_packages, None)

    assert filter_model.rowCount() == 2
    assert filter_model.index(0, 0).data() == "actdiag"
    assert filter_model.index(1, 0).data() == "apng"


def test_get_version():
    message = """
Name: xxxx
Version: 0.2.13
Summary: XXXXXXXXXXXXXXXXXXXXXX
Home-page: XXXXXXXXXXXXX
Author: XXXXXXXXXXXX
Author-email: XXXXXXXXXXXX
License: MIT
Location: XXXXXXXXXXXX
Requires: docutils, jinja2, traitlets, nbconvert, nbformat, sphinx
"""

    for line in message.splitlines():
        if line.startswith("Version: "):
            version = line[len("Version: "):].strip()
            break
    else:
        version = None

    assert version == "0.2.13"
