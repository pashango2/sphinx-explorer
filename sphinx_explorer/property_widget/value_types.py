#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from . import TypeBase
import os
from PySide.QtCore import *
from PySide.QtGui import *


class RefButtonWidget(QFrame):
    def __init__(self, parent=None):
        super(RefButtonWidget, self).__init__(parent)
        self.delegate = None
        self.line_edit = QLineEdit(self)
        self.ref_button = QToolButton(self)
        self.ref_button.setText("...")
        self.ref_button.setAutoRaise(False)
        self.ref_button.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.ref_button)

        # noinspection PyUnresolvedReferences
        self.ref_button.clicked.connect(self._onRefButtonClicked)
        self.setTabOrder(self.line_edit, self.ref_button)
        self.setFocusProxy(self.line_edit)
        self.setFocusPolicy(Qt.WheelFocus)

        self.line_edit.installEventFilter(self)

        self._block = False

    def eventFilter(self, obj, evt):
        if evt.type() == QEvent.FocusOut:
            if self._block is False:
                # noinspection PyCallByClass
                QApplication.postEvent(self, QFocusEvent(evt.type(), evt.reason()))
                return False
        return super(RefButtonWidget, self).eventFilter(obj, evt)

    def _onRefButtonClicked(self):
        self._block = True
        try:
            self.onRefButtonClicked()
        finally:
            self._block = False

    def setText(self, text):
        self.line_edit.setText(text)
        self.line_edit.selectAll()
        self.line_edit.setFocus()

    def text(self):
        return self.line_edit.text()


class PathParamWidget(RefButtonWidget):
    def onRefButtonClicked(self):
        cwd = self.line_edit.text() or os.getcwd()
        # noinspection PyCallByClass
        path_dir = QFileDialog.getExistingDirectory(
            self, "Sphinx root path", cwd
        )
        if path_dir:
            self.line_edit.setText(path_dir)


class TypeBool(TypeBase):
    @classmethod
    def control(cls, parent):
        combo = QComboBox(parent)
        combo.addItem("Yes")
        combo.addItem("No")
        return combo

    @classmethod
    def set_value(cls, control, value):
        control.setCurrentIndex(0 if value else 1)

    @classmethod
    def value(cls, control):
        return control.currentIndex() == 0

    @staticmethod
    def data(value):
        return "Yes" if value else "No"


class TypeDirPath(TypeBase):
    is_persistent_editor = True

    @classmethod
    def control(cls, parent):
        return PathParamWidget(parent)

    @classmethod
    def set_value(cls, control, value):
        control.setText(value)

    @classmethod
    def value(cls, control):
        return control.text()


class TypeChoice(TypeBase):
    def __init__(self, selects):
        self.selects = selects
        self._data_dict = {item["value"]: item for item in selects}

    def control(self, parent):
        combo = QComboBox(parent)

        for i, item in enumerate(self.selects):
            combo.addItem(item["text"])
            combo.setItemData(i, item["value"])

        return combo

    @classmethod
    def set_value(cls, combo, value):
        # type: (QComboBox, str) -> None
        index = combo.findData(value)
        combo.setCurrentIndex(index)

    @classmethod
    def value(cls, combo):
        # type: (QComboBox, str) -> None
        return combo.itemData(combo.currentIndex())

    @classmethod
    def default(cls):
        return None

    # noinspection PyMethodOverriding
    def data(self, value):
        return self._data_dict[value]["text"] if value in self._data_dict else None

    # noinspection PyMethodOverriding
    def icon(self, value):
        return self._data_dict[value]["icon"] if value in self._data_dict else None


AllTypes = [
    TypeBool,
    TypeDirPath,
]


def register_value_type(value_type):
    global AllTypes
    AllTypes.append(value_type)


def find_value_type(type_name):
    for value_type in AllTypes:
        if value_type.__name__ == type_name:
            return value_type
    return None
