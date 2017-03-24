#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *
import json
from typing import Iterator

# from .theme_dialog import ThemeDialog
# from .sphinx_analyzer import SphinxInfo

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1


class TypeBase(object):
    @staticmethod
    def data(value):
        return value

    @classmethod
    def height(cls):
        return -1

    @classmethod
    def default(cls):
        return None


class PropertyWidget(QTableView):
    def __init__(self, parent=None):
        # type: (QWidget) -> None
        super(PropertyWidget, self).__init__(parent)
        self._delegate = PropertyItemDelegate(self)
        self._model = PropertyModel(self)
        self.setModel(self._model)
        self.setItemDelegate(self._delegate)

        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

    def add_category(self, category_name):
        # type: (str) -> PropertyCategoryItem
        item = PropertyCategoryItem(category_name)
        self._model.add_category(item)
        self.setSpan(item.row(), 0, 1, 2)
        return item

    def add_property(self, key, label_name, value, value_type=None):
        # type: (str, str, any, any) -> PropertyItem
        item = PropertyItem(key, label_name, value, value_type)
        self._model.add_property(item)

        height = item.sizeHint().height()
        if height > 0:
            self.setRowHeight(item.row(), height)

        return item

    def setReadOnly(self, readonly):
        # type: (bool) -> None
        self._model.setReadOnly(readonly)

    def dump(self):
        # type: () -> dict
        result = {}
        for item in self.properties():
            if item.value is not None:
                result[item.key] = item.value
        return result

    def dumps(self):
        # type: () -> str
        return json.dumps(self.dump(), indent=4)

    def loads(self, params):
        # type: (str) -> bool
        obj = json.loads(params)
        return self.load(obj)

    def load(self, params):
        # type: (dict) -> bool
        params_dict = {x.key: x for x in self.properties()}
        for key, value in params.items():
            if key in params_dict:
                item = params_dict[key]
                item.value = value

        return True

    def properties(self):
        # type: () -> Iterator[PropertyItem]
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            if item.type() == PropertyItemType:
                yield item


class PropertyModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(PropertyModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(["Property", "Value"])
        self._readonly = False

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
        # type: (QModelIndex) -> QStandardItem
        index = self.index(index.row(), 0) if index.column() != 0 else index
        return self.itemFromIndex(index)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 1:
                index = self.index(index.row(), 0)
                item = self.itemFromIndex(index)
                if item.type() == PropertyItemType:
                    if item.value_type:
                        return item.value_type.data(item.value)
                    else:
                        return item.value

        return super(PropertyModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if index.column() == 1:
                index = self.index(index.row(), 0)
                item = self.itemFromIndex(index)
                item.value = value
                return True

        return super(PropertyModel, self).setData(index, value, role)


class PropertyCategoryItem(QStandardItem):
    @staticmethod
    def type():
        return CategoryItemType

    def __init__(self, name):
        # type: (str) -> None
        super(PropertyCategoryItem, self).__init__(name)

        self.setBackground(QBrush(QColor(71, 74, 77)))
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)


class PropertyItem(QStandardItem):
    @staticmethod
    def type():
        return PropertyItemType

    def __init__(self, key, label, value, value_type=None):
        # type: (str, any, TypeBase or None) -> None
        super(PropertyItem, self).__init__(label)
        self.key = key
        self.value = value
        self.value_type = value_type
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)

        if self.value_type and value is None:
            self.value = self.value_type.default()


class PropertyItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(PropertyItemDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        # type: (QWidget, QStyleOptionViewItem, QModelIndex) -> QWidget
        model = index.model()  # :type: PropertyModel
        item = model.rowItem(index)  # :type: PropertyItem

        if item.value_type is None:
            return super(PropertyItemDelegate, self).createEditor(parent, option, index)
        else:
            return item.value_type.control(parent)

    def setEditorData(self, editor, index):
        # type: (QWidget, QModelIndex) -> None
        model = index.model()  # :type: PropertyModel
        item = model.rowItem(index)  # :type: PropertyItem

        if item.value_type:
            item.value_type.set_value(editor, item.value)
        else:
            super(PropertyItemDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        # type: (QWidget, PropertyModel, QModelIndex) -> None
        model = index.model()  # :type: PropertyModel
        item = model.rowItem(index)  # :type: PropertyItem

        if item.value_type is None:
            super(PropertyItemDelegate, self).setModelData(editor, model, index)
        else:
            value = item.value_type.value(editor)
            model.setData(index, value, Qt.EditRole)

from .value_types import *  # NOQA
