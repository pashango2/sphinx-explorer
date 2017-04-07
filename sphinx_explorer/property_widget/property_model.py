#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .value_types import TypeBase
import os
from six import string_types
from PySide.QtCore import *
from PySide.QtGui import *

__all__ = [
    "PropertyModel",
    "PropertyCategoryItem",
    "PropertyItem",
]

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1


class PropertyCategoryItem(QStandardItem):
    BACKGROUND_COLOR = QColor(71, 74, 77)
    FOREGROUND_COLOR = QColor(0xFF, 0xFF, 0xFF)

    @staticmethod
    def type():
        return CategoryItemType

    def __init__(self, name):
        # type: (str) -> None
        super(PropertyCategoryItem, self).__init__(name)

        self.setBackground(QBrush(self.BACKGROUND_COLOR))
        self.setForeground(self.FOREGROUND_COLOR)
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        # self.setFlags(self.flags() & ~(Qt.ItemIsEditable | Qt.ItemIsSelectable))
        self.setFlags(Qt.NoItemFlags)
        self.setEnabled(True)


class PropertyItem(QStandardItem):
    @staticmethod
    def type():
        return PropertyItemType

    def __init__(self, key, label, value, description, value_type=None):
        # type: (string_types, string_types, any, string_types, TypeBase) -> None
        super(PropertyItem, self).__init__(label)
        self.key = key
        self._value = value
        self.description = description
        self.value_type = value_type
        self.setFlags(Qt.NoItemFlags)
        self.setEnabled(True)
        self.validator = None
        self._link = None
        self._link_format = None
        self._linked = []
        self._default_flag = value is None
        self._default = None
        self._required = False

    def set_required(self, required):
        self._required = required

    def set_indent(self, indent):
        # type: (int) -> None
        self.setText(("    " * indent) + self.text())

    def set_validator(self, validator):
        # type: (QValidator) -> None
        self.validator = validator

    def set_value(self, value):
        # (Any) -> None
        if value == self._default:
            return

        self._value = value
        self._default_flag = self.value is None

        for linked in self._linked:
            linked.update_link(value)

    def update_link(self, value=None):
        # (Any) -> None
        if self._link is None:
            return

        value = value or self._link.value
        self._default = self.value_type.default(value)

    def update_default(self):
        self._default = self.model().default_value(self.key)

    @property
    def value(self):
        # type: () -> any
        if self._value is not None:
            return self._value
        else:
            return self._default

    def was_default(self):
        # type: () -> bool
        return self._default_flag

    def set_link(self, link, link_format=None):
        # type: (PropertyItem or None, str or None) -> None
        if link is None:
            return

        self._link = link
        self._link_format = link_format
        # noinspection PyProtectedMember
        link._linked.append(self)
        self.update_link(link.value)

    def is_complete(self):
        # type: () -> bool
        if not self.value and self._required:
            return False

        return True


class PropertyModel(QStandardItemModel):
    DEFAULT_VALUE_FOREGROUND_COLOR = QColor(0x80, 0x80, 0x80)

    def __init__(self, parent=None):
        super(PropertyModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(["Property", "Value"])
        self._readonly = False
        self._use_default = False
        self._default_dict = {}

    def set_default_dict(self, default_dict):
        # (dict) -> None
        self._default_dict = default_dict.copy()
        self._use_default = bool(default_dict)

    def set_use_default(self, use_default):
        # (bool) -> None
        self._use_default = use_default

    def default_value(self, key):
        # (string_types) -> any
        return self._default_dict.get(key)

    def set_default_value(self, key, value, update=True):
        # type: (string_types, any, bool) -> None
        if not update and key in self._default_dict:
            return
        self._default_dict[key] = value

    def add_category(self, item):
        # type: (PropertyCategoryItem) -> None
        self.appendRow(item)

    def add_property(self, item):
        # type: (PropertyItem) -> None
        self.appendRow(item)

    def setReadOnly(self, readonly):
        # type: (bool) -> None
        self._readonly = readonly

    def rowItem(self, index):
        # type: (QModelIndex) -> PropertyItem
        index = self.index(index.row(), 0) if index.column() != 0 else index
        return self.itemFromIndex(index)

    def _property_item(self, index):
        # type: (QModelIndex) -> PropertyItem or None
        if not index.isValid():
            return None

        item = self.item(index.row(), 0)
        if item.type() == PropertyItemType:
            return item
        return None

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 1:
                item = self._property_item(index)
                if item:
                    value = item.value
                    if not value:
                        value = self._default_dict.get(item.key)
                    return item.value_type.data(value) if item.value_type else value
        elif role == Qt.DecorationRole:
            if index.column() == 1:
                item = self._property_item(index)
                if item:
                    if item.value_type:
                        return item.value_type.icon(item.value)
        elif role == Qt.ForegroundRole:
            if index.column() == 1:
                item = self._property_item(index)
                if item:
                    if item.was_default():
                        return self.DEFAULT_VALUE_FOREGROUND_COLOR

        return super(PropertyModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if index.column() == 1:
                index = self.index(index.row(), 0)
                item = self.itemFromIndex(index)
                item.set_value(value)
                # noinspection PyUnresolvedReferences
                self.itemChanged.emit(item)
                return True

        return super(PropertyModel, self).setData(index, value, role)
