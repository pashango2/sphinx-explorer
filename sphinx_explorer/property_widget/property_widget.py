#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import json
from .property_model import PropertyModel, CategoryItem, PropertyItem
from .define import PropertyItemType
from six import string_types

if False:
    from typing import Dict, Iterator


class PropertyWidget(QTableView):
    """
    Widget to edit properties collectively.

    * Dynamic property settings.
    * Hierarchical setting of default values
    """
    itemChanged = Signal(QStandardItem)

    def __init__(self, parent=None, model=None):
        # type: (QWidget, PropertyModel) -> None
        super(PropertyWidget, self).__init__(parent)
        self._model = model
        self.selection_model = None
        self._first_property_index = QModelIndex()

        self._delegate = PropertyItemDelegate(self)
        self.setItemDelegate(self._delegate)

        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.setTabKeyNavigation(False)

        self.setModel(self._model)

    def setModel(self, model):
        self._model = model

        if model:
            super(PropertyWidget, self).setModel(model)
            # self._connect()
            self.selection_model = self.selectionModel()
            self.setup()

    def setRootIndex(self, index):
        super(PropertyWidget, self).setRootIndex(index)
        self.setup()

    def setup(self):
        self.clearSpans()
        self._first_property_index = QModelIndex()

        for row in range(self._model.rowCount(self.rootIndex())):
            index = self._model.index(row, 0, self.rootIndex())
            item = self._model.itemFromIndex(index)

            if item is None:
                continue

            if item.is_category:
                self.setSpan(row, 0, 1, 2)

            if not self._first_property_index.isValid():
                self._first_property_index = self.index(row, 1, self.rootIndex())

            if not item.is_category and item.value_type and item.value_type.is_persistent_editor:
                value_index = index.sibling(index.row(), 1)
                self.openPersistentEditor(value_index)
                ctrl = self.indexWidget(value_index)
                item.value_type.set_value(ctrl, item.value)

        # self.setCurrentIndex(self._first_property_index)
        self.resizeRowsToContents()
        self.resizeColumnToContents(0)

    def teardown(self):
        for row in range(self._model.rowCount(self.rootIndex())):
            index = self._model.index(row, 0, self.rootIndex())
            item = self._model.itemFromIndex(index)

            if not item.is_category and item.value_type and item.value_type.is_persistent_editor:
                value_index = index.sibling(index.row(), 1)
                ctrl = self.indexWidget(value_index)
                if ctrl:
                    item.set_value(item.value_type.value(ctrl))

                # self.closePersistentEditor(value_index)

    def clear(self):
        self._model.removeRows(0, self._model.rowCount())

    def index(self, row, column, parent=QModelIndex()):
        # type: (int, int) -> QModelIndex
        return self._model.index(row, column, parent)

    def add_category(self, key, name=None):
        # type: (string_types, string_types) -> CategoryItem
        name = name or key
        item = self._model.add_category(key, name)
        self.setSpan(item.row(), 0, 1, 2)
        return item

    def add_property(self, parent_item, item_key, params, label_name=None):
        # type: (str, dict, str or None) -> PropertyItem
        item = self._model.add_property(parent_item, item_key, params, label_name)

        if not self._first_property_index.isValid():
            self._first_property_index = self.index(item.row(), 1)

        return item

    def get(self, keys):
        return self._model.get(keys)

    def first_property_index(self):
        # type: () -> QModelIndex
        return self._first_property_index

    def setReadOnly(self, readonly):
        # type: (bool) -> None
        if readonly:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.setEditTriggers(QAbstractItemView.AllEditTriggers)

    def dump(self, flat=False, exclude_default=False):
        # type: () -> dict
        self.teardown()
        return self._model.dump(flat=flat, exclude_default=exclude_default)

    def dumps(self):
        # type: () -> str
        self.teardown()
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
                item.set_value(value, force_update=True)
        return True

    def load_settings(self, settings, params_dict=None):
        # (dict, dict or None) -> None
        self._model.load_settings(settings, params_dict)

    def property_map(self):
        # type: () -> Dict[string_types, PropertyItem]
        return self._model.property_map()

    def item(self, name):
        # type: (string_types) -> PropertyItem
        return self.property_map().get(name)

    def properties(self, root_index=None):
        # type: (QModelIndex) -> Iterator[PropertyItem]
        return self._model.properties(root_index)

    def description(self, index):
        # type: (QModelIndex) -> str or None
        if not index.isValid():
            return None, None

        index = index.sibling(index.row(), 0)
        item = self._model.itemFromIndex(index)
        if item.type() == PropertyItemType:
            return item.description, item.description_path
        return None, None

    def title(self, index):
        # type: (QModelIndex) -> str or None
        if not index.isValid():
            return None

        index = index.sibling(index.row(), 0)
        item = self._model.itemFromIndex(index)
        return item.text() if item else ""

    # def closeEditor(self, editor, _):
    #     super(PropertyWidget, self).closeEditor(editor, QAbstractItemDelegate.EditNextItem)

    # noinspection PyMethodOverriding
    def moveCursor(self, action, modifiers):
        if action == QAbstractItemView.MoveNext:
            action = QAbstractItemView.MoveDown
        elif action == QAbstractItemView.MovePrevious:
            action = QAbstractItemView.MoveUp

        return super(PropertyWidget, self).moveCursor(action, modifiers)

    def is_complete(self):
        # type: () -> bool
        return self._model.is_complete(self.rootIndex())

    def update_link(self):
        for property_item in self.properties():
            property_item.update_link()

    def set_default_value(self, key, value, update=True):
        self._model.set_default_value(key, value, update)
        self.update_default()

    def set_values(self, values_dict):
        self._model.set_values(values_dict)

    def default_value(self, key):
        return self._model.default_value(key)

    def update_default(self):

        for prop in self.properties():
            prop.update_link()


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
            return item.value_type.control(self, item, parent)

    def setEditorData(self, editor, index):
        # type: (QWidget, QModelIndex) -> None
        model = index.model()  # :type: ProtpertyModel
        item = model.itemFromIndex(index)  # :type: PropertyItem

        if item.value_type:
            item.value_type.set_value(editor, item.value)
        else:
            super(PropertyItemDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        # type: (QWidget, PropertyModel, QModelIndex) -> None
        item = model.rowItem(index)  # :type: PropertyItem

        if item.value_type is None:
            super(PropertyItemDelegate, self).setModelData(editor, model, index)
        else:
            value = item.value_type.value(editor)
            model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
