#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
import markdown
# noinspection PyUnresolvedReferences
from six import string_types
# noinspection PyUnresolvedReferences
from PySide.QtCore import *
from PySide.QtGui import *
from typing import Iterator
from .property_model import PropertyItem, PropertyCategoryItem, PropertyModel
from .property_model import PropertyItemType

__all__ = [
    "PropertyWidget",
]

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

    def set_default_dict(self, default_dict):
        self._model.set_default_dict(default_dict)

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

    def create_property(self, item_key, params):
        # type: (str, dict) -> PropertyItem
        label_name = params.get("name")
        value = params.get("value")
        description = params.get("description")
        value_type = params.get("value_type")

        if isinstance(value_type, string_types):
            value_type = find_value_type(value_type)

        item = PropertyItem(item_key, label_name, value, description, value_type)

        if "default" in params:
            self._model.set_default_value(item_key, params["default"], update=False)
        item.update_link(self._model.default_value(item_key))

        if params.get("description"):
            item.setToolTip(params.get("description").strip())

        return item

    def add_property_item(self, item):
        # type: (PropertyItem) -> None
        self._model.add_property(item)

        height = item.sizeHint().height()
        if height > 0:
            self.setRowHeight(item.row(), height)

    def add_property(self, item_key, params):
        # type: (str, dict) -> PropertyItem
        item = self.create_property(item_key, params)
        self.add_property_item(item)
        return item

    def setReadOnly(self, readonly):
        # type: (bool) -> None
        if readonly:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.setEditTriggers(QAbstractItemView.AllEditTriggers)

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
                item.set_value(value)
        return True

    def _load_settings(self, settings):
        props = []

        for key, value in settings.items():
            name = value.get("name")
            if name is None or isinstance(name, dict):
                self.add_category(key)
                props += self._load_settings(value)
            else:
                item = self.add_property(key, value)
                props.append((value, item))

        return props

    def load_settings(self, settings, default_value=None):
        # (dict) -> [PropertyItem]
        if default_value:
            self._model.set_default_dict(default_value)

        props = self._load_settings(settings)
        prop_map = self.property_map()

        for value, item in props:
            if "link" in value:
                item.set_link(prop_map.get(value["link"]), value.get("link_format"))

        return [_[1] for _ in props]

    def property_map(self):
        return {
            item.key: item
            for item in self.properties()
            }

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
        dec = self.description(index)
        if dec:
            md = """
            {}
            """.strip().format(dec)

            mdo = markdown.Markdown(extensions=["gfm"])
            html = CssStyle + mdo.convert(md)
            return html

        return None

    def closeEditor(self, editor, _):
        super(PropertyWidget, self).closeEditor(editor, QAbstractItemDelegate.EditNextItem)

    def moveCursor(self, action, modifiers):
        if action == QAbstractItemView.MoveNext:
            action = QAbstractItemView.MoveDown
        elif action == QAbstractItemView.MovePrevious:
            action = QAbstractItemView.MoveUp

        return super(PropertyWidget, self).moveCursor(action, modifiers)


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
