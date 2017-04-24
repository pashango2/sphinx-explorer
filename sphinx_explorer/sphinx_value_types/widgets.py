#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *

import os

from sphinx_explorer.property_widget import cog_icon
from sphinx_explorer.property_widget.widgets import MovableListWidget
from sphinx_explorer.util.python_venv import check_python_version


class ComboButton(QFrame):
    def __init__(self, parent=None):
        super(ComboButton, self).__init__(parent)

        self.combo_box = QComboBox(self)
        self.tool_button = QToolButton(self)
        self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tool_button.setText("setting")
        self.tool_button.setIcon(cog_icon())

        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.tool_button)
        self.setLayout(self.layout)

    def findData(self, *args, **kwargs):
        return self.combo_box.findData(*args, **kwargs)

    def currentIndex(self):
        return self.combo_box.currentIndex()

    def setCurrentIndex(self, index):
        self.combo_box.setCurrentIndex(index)

    def itemData(self, *args):
        return self.combo_box.itemData(*args)


class PythonComboButton(ComboButton):
    def __init__(self, parent=None):
        super(PythonComboButton, self).__init__(parent)

        self.add_path_act = QAction("Add Path", self, triggered=self._on_add_path)
        self.menu = QMenu(self)
        self.menu.addAction(self.add_path_act)

        self.tool_button.setMenu(self.menu)
        self.tool_button.setPopupMode(QToolButton.InstantPopup)

    def _on_add_path(self):
        dlg = PythonEnvDialog(self)

        if dlg.exec_() == QDialog.Accepted:
            path_list = dlg.dump()


class PythonEnvDialog(QDialog):
    def __init__(self, parent=None):
        super(PythonEnvDialog, self).__init__(parent)

        self.list_widget = MovableListWidget(self)
        self.list_widget.input_value_callback = self.input_value

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        self.resize(492, 652)

    def input_value(self):
        # noinspection PyCallByClass,PyArgumentList
        path = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Python Exe"),
            os.path.expanduser('~'),
        )[0]

        v = check_python_version(path)
        return path if v else None

    def dump(self):
        result = []

        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            result.append(item.text())

        return result



