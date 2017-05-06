#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os

from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
from six import string_types

from ..widgets import PathParamWidget, RelPathParamWidget, FilePathWidget


class TypeBase(object):
    @classmethod
    def create(cls, _):
        """
        Create instance or return class
        """
        return cls

    @classmethod
    def control(cls, delegate, property_item, parent):
        return None

    @staticmethod
    def data(value):
        """
        return item's data() value
        """
        return value

    @classmethod
    def value(cls, control):
        return None

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

    @classmethod
    def set_value(cls, control, value):
        control.setText(value)

    is_persistent_editor = False


class TypeBool(TypeBase):
    @classmethod
    def control(cls, delegate, property_item, parent):
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


class CheckBox(QCheckBox):
    def __init__(self, item, parent):
        super(CheckBox, self).__init__(parent)
        self.item = item
        # noinspection PyUnresolvedReferences
        self.stateChanged.connect(self.on_state_changed)

    def on_state_changed(self, state):
        self.item.set_value(state == Qt.Checked, force_update=True)


class TypeCheck(TypeBase):
    is_persistent_editor = True

    @classmethod
    def control(cls, delegate, property_item, parent):
        check = CheckBox(property_item, parent)
        return check

    @classmethod
    def set_value(cls, control, value):
        # type: (QCheckBox, bool) -> None
        control.setCheckState(Qt.Checked if value else Qt.Unchecked)

    @classmethod
    def value(cls, control):
        # type: (QCheckBox) -> bool
        return control.isChecked()


class TypeFilePath(TypeBase):
    @classmethod
    def control(cls, delegate, property_item, parent):
        return FilePathWidget(delegate, property_item.params, parent=parent)

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

    @classmethod
    def sizeHint(cls):
        return QSize(-1, 28)


class TypeDirPath(TypeBase):
    @classmethod
    def control(cls, delegate, property_item, parent):
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

    @classmethod
    def sizeHint(cls):
        return QSize(-1, 28)


class TypeRelDirPath(TypeDirPath):
    @classmethod
    def create(cls, params):
        return cls(params)

    def __init__(self, params):
        self.relpath = params.get("relpath", ".")

    def control(self, delegate, property_item, parent):
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


# noinspection PyArgumentList
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

    def control(self, delegate, property_item, parent):
        combo = QComboBox(parent)
        self.setup_combo_box(combo)
        return combo

    def setup_combo_box(self, combo):
        for i, item in enumerate(self.selects):
            combo.addItem(item["text"])
            combo.setItemData(i, item["value"])
            if "icon" in item:
                combo.setItemIcon(i, item["icon"])

    # noinspection PyMethodOverriding
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
