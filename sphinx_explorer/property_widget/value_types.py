#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from six import string_types
from PySide.QtCore import *
from PySide.QtGui import *
from . import define


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

    def __init__(self, selects):
        self.selects = []

        for item in selects:
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

    @classmethod
    def set_value(cls, combo, value):
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


class TypeFontList(TypeBase):
    @classmethod
    def control(cls, _, parent):
        return FontListWidget(parent)

    @classmethod
    def value(cls, control):
        return "FONT\nFONT2\nFONT3"

    @classmethod
    def set_value(cls, control, value):
        # type: (FontListWidget, string_types) -> None
        print(value)
        value = value or ""
        control.addItems(value.splitlines())

    @classmethod
    def sizeHint(cls):
        return QSize(-1, 200)

    @classmethod
    def setup(cls, item):
        item.setData(Qt.AlignTop | Qt.AlignLeft, Qt.TextAlignmentRole)


class FontListWidget(QListWidget):
    TOOL_WIDTH = 42

    def __init__(self, parent=None):
        super(FontListWidget, self).__init__(parent)
        self.frame = QFrame(self)
        self.tool_layout = QVBoxLayout(self.frame)
        self.tool_layout.setContentsMargins(0, 0, 0, 0)
        self.tool_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.add_act = QAction(define.ADD_ICON, "Add", self)
        self.up_act = QAction(define.UP_ICON, "Add", self)
        self.down_act = QAction(define.DOWN_ICON, "Add", self)
        self.del_act = QAction(define.DELETE_ICON, "Add", self)
        self.actions = [self.add_act, self.up_act, self.down_act, self.del_act]

        for act in self.actions:
            button = QToolButton(self)
            button.setDefaultAction(act)
            self.tool_layout.addWidget(button)

        self.frame.setLayout(self.tool_layout)

    def _on_add(self):
        font = QFontDialog.getFont()

    def resizeEvent(self, evt):
        width = self.size().width()
        height = self.size().height()

        self.frame.setGeometry(
            width - self.TOOL_WIDTH, 0,
            self.TOOL_WIDTH, height
        )
        print(self.rect())
        return super(FontListWidget, self).resizeEvent(evt)


AllTypes = [
    TypeBool,
    TypeDirPath,
    TypeRelDirPath,
    TypeChoice,
    TypeFontList,
]


def register_value_type(value_type):
    # type: (TypeBase) -> None
    global AllTypes
    AllTypes.append(value_type)


def find_value_type(type_name, params=None):
    # type: (string_types, dict or None) -> TypeBase or None
    for value_type in AllTypes:
        if value_type.__name__ == type_name:
            return value_type.create(params)
    return None
