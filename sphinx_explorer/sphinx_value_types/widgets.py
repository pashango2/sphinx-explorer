#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os

from qtpy.QtWidgets import *

from sphinx_explorer.property_widget import cog_icon
from sphinx_explorer.property_widget.widgets import MovableListWidget
from sphinx_explorer.python_venv import check_python_version, VenvSetting


# noinspection PyArgumentList
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


# noinspection PyArgumentList
class PythonComboButton(ComboButton):
    def __init__(self, parent=None):
        super(PythonComboButton, self).__init__(parent)

        # noinspection PyArgumentList
        self.add_path_act = QAction("Add Path", self, triggered=self._on_add_path)
        self.menu = QMenu(self)
        self.menu.addAction(self.add_path_act)

        self.tool_button.setMenu(self.menu)
        self.tool_button.setPopupMode(QToolButton.InstantPopup)

        self.venv_setting = VenvSetting()

        self.default_index = -1

    def setup(self, value=None):
        self.venv_setting = VenvSetting(value)
        idx = self.combo_box.findData(self.venv_setting.env)
        self.combo_box.setCurrentIndex(idx)

    def set_value(self, venv_setting):
        # type: (VenvSetting) -> None
        self.venv_setting = venv_setting
        idx = self.combo_box.findData(self.venv_setting.env)
        self.setCurrentIndex(idx)

    def value(self):
        return VenvSetting({
            "env": self.itemData(self.currentIndex()),
            "search_venv_path": self.venv_setting.search_venv_path,
        })

    def _on_add_path(self):
        dlg = PythonEnvDialog(self)
        dlg.setup(self.venv_setting.search_venv_path)

        if dlg.exec_() == QDialog.Accepted:
            self.venv_setting.set_search_venv_path(dlg.dump())

    def setCurrentIndex(self, index):
        if index == -1:
            if self.default_index != -1:
                self.combo_box.setCurrentIndex(index)
            else:
                self.combo_box.setCurrentIndex(0)
        else:
            self.combo_box.setCurrentIndex(index)


# noinspection PyArgumentList
class PythonEnvDialog(QDialog):
    # noinspection PyUnresolvedReferences
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
        # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
        path = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Python Exe"),
            os.path.expanduser('~'),
        )[0]

        v = check_python_version(path)
        return path if v else None

    def setup(self, path_list):
        for path in path_list:
            self.list_widget.addItem(path)

    def dump(self):
        result = []

        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            result.append(item.text())

        return result


