#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from six import string_types
from PySide.QtCore import *
from PySide.QtGui import *


class TypeBase(object):
    @classmethod
    def create(cls, _):
        return cls

    @staticmethod
    def data(value):
        return value

    @staticmethod
    def icon(_):
        return None

    @classmethod
    def height(cls):
        return -1

    @classmethod
    def default(cls, value):
        return value

    @classmethod
    def control(cls, delegate, parent):
        return None

    @classmethod
    def filter(cls, value):
        return value

    @classmethod
    def set_link(cls, value):
        pass

    @classmethod
    def link_value(cls, default_value, link_value):
        return link_value or default_value

    @classmethod
    def sizeHint(cls):
        return QSize(-1, -1)

    @classmethod
    def setup(cls, item):
        pass

    is_persistent_editor = False


class RefButtonWidget(QFrame):
    def __init__(self, parent=None):
        super(RefButtonWidget, self).__init__(parent)
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
    def __init__(self, delegate, params=None, parent=None):
        super(PathParamWidget, self).__init__(parent)
        params = params or {}
        self.delegate = delegate
        self.title = params.get("selector_title", "Select directory")

    def onRefButtonClicked(self):
        path_dir = self.get_path()
        if path_dir:
            self.setText(path_dir)
            self.closeEditor()

    def closeEditor(self):
        if self.delegate:
            self.delegate.commitData.emit(self)
            self.delegate.closeEditor.emit(self, QAbstractItemDelegate.EditNextItem)

    def get_path(self, cwd=None):
        cwd = cwd or self.line_edit.text() or os.getcwd()
        # noinspection PyCallByClass
        path_dir = QFileDialog.getExistingDirectory(
            self, self.title, cwd
        )
        return path_dir


class RelPathParamWidget(PathParamWidget):
    def __init__(self, delegate, relpath, params=None, parent=None):
        super(RelPathParamWidget, self).__init__(delegate, params, parent)
        self.relpath = relpath

    def onRefButtonClicked(self):
        path_dir = self.get_path(self.relpath)
        if path_dir:
            if self.relpath:
                try:
                    path_dir = os.path.relpath(path_dir, self.relpath)
                    path_dir = path_dir.replace(os.path.sep, "/")
                except ValueError:
                    pass
            self.setText(path_dir)
            self.closeEditor()


class TypeBool(TypeBase):
    @classmethod
    def control(cls, delegate, parent):
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
    @classmethod
    def control(cls, delegate, parent):
        return PathParamWidget(delegate, parent=parent)

    @classmethod
    def set_value(cls, control, value):
        control.setText(value)

    @classmethod
    def value(cls, control):
        return control.text()

    @classmethod
    def filter(cls, value):
        return os.path.normpath(value) if value else value

    @classmethod
    def link_value(cls, default_value, link_value):
        if default_value is None and link_value is None:
            return ""
        if link_value is None:
            return default_value
        if default_value is None:
            return link_value
        return os.path.join(default_value, link_value)


class TypeRelDirPath(TypeDirPath):
    @classmethod
    def create(cls, params):
        return cls(params)

    def __init__(self, params):
        self.relpath = params.get("relpath", ".")

    def control(self, delegate, parent):
        return RelPathParamWidget(delegate, relpath=self.relpath, parent=parent)

    def default(self, path):
        self.relpath = path or "."
        return "."

    def set_link(self, value):
        self.relpath = value or "."

    def filter(self, value):
        if not value:
            return "."
        try:
            if os.path.isabs(value):
                return os.path.relpath(value, self.relpath)
            else:
                return value
        except ValueError:
            return "."


class TypeChoice(TypeBase):
    @classmethod
    def create(cls, params):
        return cls(params.get("choices", []))

    def __init__(self, choices):
        self.selects = []
        self._data_dict = {}
        self.setup_choices(choices)

    def setup_choices(self, choices):
        self.selects = []

        for item in choices:
            if isinstance(item, string_types):
                item = {
                    "text": item,
                    "value": item,
                }
            self.selects.append(item)
        self._data_dict = {item["value"]: item for item in self.selects}

    def control(self, delegate, parent):
        combo = QComboBox(parent)

        for i, item in enumerate(self.selects):
            combo.addItem(item["text"])
            combo.setItemData(i, item["value"])

        return combo

    @staticmethod
    def set_value(combo, value):
        # type: (QComboBox, str) -> None
        index = combo.findData(value)
        combo.setCurrentIndex(index)

    @classmethod
    def value(cls, combo):
        # type: (QComboBox, str) -> None
        return combo.itemData(combo.currentIndex())

    # noinspection PyMethodOverriding
    def data(self, value):
        return self._data_dict[value]["text"] if value in self._data_dict else None

    # noinspection PyMethodOverriding
    def icon(self, value):
        try:
            return self._data_dict[value]["icon"] if value in self._data_dict else None
        except KeyError:
            return None
