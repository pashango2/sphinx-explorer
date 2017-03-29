#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# noinspection PyUnresolvedReferences
from PySide.QtCore import *
from PySide.QtGui import *
import json
from typing import Iterator
import markdown

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1

CssStyle = """
<style>
a {color: #4183C4; }
a.absent {color: #cc0000; }
a.anchor {
  display: block;
  padding-left: 30px;
  margin-left: -30px;
  cursor: pointer;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0; }

</style>
"""


class TypeBase(object):
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
    def default(cls):
        return None

    is_persistent_editor = False


class PropertyWidget(QTableView):
    currentChanged = Signal(QModelIndex, QModelIndex)

    def __init__(self, parent=None):
        # type: (QWidget) -> None
        super(PropertyWidget, self).__init__(parent)
        self._delegate = PropertyItemDelegate(self)
        self._model = PropertyModel(self)
        self.setModel(self._model)
        self.selection_model = self.selectionModel()
        self.selection_model.currentChanged.connect(self.currentChanged.emit)
        self.setItemDelegate(self._delegate)

        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.setTabKeyNavigation(False)

        self._default_dict = {}

    def set_default_dict(self, default_dict):
        self._default_dict = default_dict

    def clear(self):
        self._model.removeRows(0, self._model.rowCount())

    def index(self, row, column):
        # type: (int, int) -> QModelIndex
        return self._model.index(row, column)

    def add_category(self, category_name):
        # type: (str) -> PropertyCategoryItem
        item = PropertyCategoryItem(category_name)
        self._model.add_category(item)
        self.setSpan(item.row(), 0, 1, 2)
        return item

    @staticmethod
    def create_property(key, label_name, value, description, value_type):
        # type: (str, str, any, any) -> PropertyItem
        return PropertyItem(key, label_name, value, description, value_type)

    def add_property_item(self, item):
        # type: (PropertyItem) -> None
        self._model.add_property(item)

        if item.value is None and item.key in self._default_dict:
            item.value = self._default_dict[item.key]

        height = item.sizeHint().height()
        if height > 0:
            self.setRowHeight(item.row(), height)

    def add_property(self, key, label_name, value, description=None, value_type=None):
        # type: (str, str, any, any) -> PropertyItem
        item = self.create_property(key, label_name, value, description, value_type)
        self.add_property_item(item)
        return item

    def setReadOnly(self, readonly):
        # type: (bool) -> None
        if readonly:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)

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

    def description(self, index):
        # type: (QModelIndex) -> str or None
        if not index.isValid():
            return None

        item = self._model.item(index.row())
        if item.type() == PropertyItemType:
            return item.description
        return None

    def html(self, index):
        # type: (QModelIndex) -> str or None
        description = self.description(index)
        if description:
            md = """
            {}
            """.strip().format(description)

            mdo = markdown.Markdown(extensions=["gfm"])
            html = CssStyle + mdo.convert(md)
            return html

        return None

    def closeEditor(self, editor, hint):
        # super(PropertyWidget, self).closeEditor(editor, hint)
        super(PropertyWidget, self).closeEditor(editor, QAbstractItemDelegate.EditNextItem)

    def moveCursor(self, action, modifiers):
        if action == QAbstractItemView.MoveNext:
            action = QAbstractItemView.MoveDown
        elif action == QAbstractItemView.MovePrevious:
            action = QAbstractItemView.MoveUp
        
        return super(PropertyWidget, self).moveCursor(action, modifiers)

    def validate(self):
        # type: () -> bool
        return True


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
                    if item.value_type:
                        return item.value_type.data(item.value)
                    else:
                        return item.value
        elif role == Qt.DecorationRole:
            if index.column() == 1:
                item = self._property_item(index)
                if item:
                    if item.value_type:
                        return item.value_type.icon(item.value)

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
        # self.setFlags(self.flags() & ~(Qt.ItemIsEditable | Qt.ItemIsSelectable))
        self.setFlags(Qt.NoItemFlags)
        self.setEnabled(True)


class PropertyItem(QStandardItem):
    @staticmethod
    def type():
        return PropertyItemType

    def __init__(self, key, label, value, description, value_type=None):
        # type: (str, any, str, TypeBase or None) -> None
        super(PropertyItem, self).__init__(label)
        self.key = key
        self.value = value
        self.description = description
        self.value_type = value_type
        self.setFlags(Qt.NoItemFlags)
        self.setEnabled(True)

        if self.value_type and value is None:
            self.value = self.value_type.default()

    def set_indent(self, indent):
        # type: (int) -> None
        self.setText(("    " * indent) + self.text())


class PropertyItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(PropertyItemDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        # type: (QWidget, QStyleOptionViewItem, QModelIndex) -> QWidget or None
        model = index.model()  # :type: PropertyModel
        item = model.rowItem(index)  # :type: PropertyItem

        if item.type() != PropertyItemType:
            return None

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
