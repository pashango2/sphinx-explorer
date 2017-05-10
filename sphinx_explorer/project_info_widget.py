#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from .ui.main_window_ui import Ui_MainWindow
from .sphinx_value_types.widgets import PythonComboButton


class ProjectInfoWidget(QObject):
    def __init__(self, ui, parent):
        super(ProjectInfoWidget, self).__init__(parent)
        self._parent = parent
        self.ui = ui

        self.setup()

    # noinspection PyAttributeOutsideInit
    def setup(self):
        # type: (Ui_MainWindow) -> None
        self.python_combo = PythonComboButton(self._parent)

        self.ui.project_info_form_layout.addRow(
            self.tr("Python Interpreter"),
            self.python_combo,
        )

        self.ui.project_info_form_layout.addRow(
            self.tr("Api Module"),
            QLabel("", self._parent),
        )

    pass

