#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.py_config import ConfigModel
from sphinx_explorer.py_config import WizardPages
import sys
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtTest import *
from qtpy.QtTest import *


def test_page():
    yaml_string = """
- "#project_settings":
    label: "Project Settings"
-
    - project:
        label: Project Name
        type: string
        required: true
    - author:
        type: string
        default: author name
    - version:
        type: string
    - release:
        type: string
        link: "project_settings.version"
- "# Project Path"
-
    - path:
        label: Project Path
        type: string
        link: "project_settings.project"
    """.strip()

    # app = QApplication(sys.argv)
    config = ConfigModel.from_yaml_string(yaml_string)
    # wizard = QWizard()
    #
    # pages = WizardPages(config, wizard)
    # for page in pages.setup():
    #     wizard.addPage(page)

    # next_button = wizard.button(QWizard.NextButton)
    # QTest.mouseClick(next_button, Qt.LeftButton)
    # wizard.exec_()




