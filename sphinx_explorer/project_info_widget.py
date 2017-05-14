#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from .ui.main_window_ui import Ui_MainWindow
from .sphinx_value_types.widgets import PythonComboButton
from .project_list_model import ProjectItem


class ProjectInfoWidget(QObject):
    def __init__(self, ui, parent):
        super(ProjectInfoWidget, self).__init__(parent)
        self._parent = parent
        self.ui = ui

        # self.python_combo = PythonComboButton(self._parent)
        #
        # self.ui.project_info_form_layout.addRow(
        #     self.tr("Python Interpreter"),
        #     self.python_combo,
        # )
        #

    def setup(self, project_item):
        # type: (ProjectItem) -> None
        if project_item and project_item.is_valid():
            self.ui.label_project.setText(project_item.project())
            self.ui.label_path.setText(project_item.path())
            self.ui.project_tool_widget.setEnabled(True)
        else:
            self.ui.label_project.clear()

            self.ui.project_tool_widget.setEnabled(False)

        widget = self.ui.tree_widget_extensions
        widget.clear()
        for ext, value in project_item.settings.extensions.items():
            widget.addExtension(ext)


