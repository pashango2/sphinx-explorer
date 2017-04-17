#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .value_types import find_value_type, TypeBase
from six import string_types
from PySide.QtCore import *
from .default_value_dict import DefaultValues
from .property_filter_model import PropertyFilterModel
from collections import OrderedDict
import markdown
from PySide.QtGui import *

__all__ = [
    "PropertyModel",
    "CategoryItem",
    "PropertyItem",
]

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1


class ValueItem(object):
    def __init__(self, value):
        self.value = value
        self._linked = []


class PropertyModel2(QStandardItemModel):
    DEFAULT_VALUE_FOREGROUND_COLOR = QColor(0x80, 0x80, 0x80)

    def __init__(self, parent=None):
        super(PropertyModel2, self).__init__(parent)
        self.setHorizontalHeaderLabels(["Property", "Value"])

    def _load_settings(self, settings, parent_item, params_dict):
        last_item = None
        for setting in settings:
            if isinstance(setting, dict):
                key = setting.keys()[0]
                setting_param = setting.values()[0][0]
            if isinstance(setting, (list, tuple)):
                assert last_item is not None
                self._load_settings(setting, last_item, params_dict)
                continue
            elif isinstance(setting, string_types):
                key = setting.strip()
                setting_param = {}

            if not key:
                continue

            if key[0] == "#":
                label = setting_param.get("label", key[1:].strip())
                last_item = self.create_category(key, label)
                parent_item.appendRow(last_item)
            else:
                last_item = self.create_property(key, setting_param)
                parent_item.appendRow(last_item)

    def load_settings(self, settings, params_dict=None):
        root_item = self.invisibleRootItem()
        self._load_settings(settings, root_item, params_dict)

    @staticmethod
    def create_category(key, label):
        # type: (string_types, string_types) -> CategoryItem
        return CategoryItem(key, label)

    @staticmethod
    def create_property(key, params):
        return PropertyItem(
            key,
            params.get("label", key),
            params.get("value"),
            params
        )

    def add_property(self, parent_item, *args, **kwargs):
        item = self.create_property(*args, **kwargs)
        if item:
            parent_item.appendRow(item)

    def rowItem(self, index):
        # type: (QModelIndex) -> PropertyItem
        index = self.index(index.row(), 0, index.parent()) if index.column() != 0 else index
        return self.itemFromIndex(index)

    def _property_item(self, index):
        # type: (QModelIndex) -> PropertyItem or None
        if not index.isValid():
            return None

        item = self.itemFromIndex(self.index(index.row(), 0, index.parent()))
        if item.type() == PropertyItemType:
            return item
        return None

    def get(self, keys):
        if isinstance(keys, string_types):
            keys = (keys,)

        parent = self.invisibleRootItem()
        for key in keys:
            for row in range(parent.rowCount()):
                item = parent.child(row)
                if item.key == key:
                    parent = item
                    break
            else:
                return None

        return parent

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 1:
                item = self._property_item(index)
                if item:
                    value = item.value
                    if value is None:
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

        return super(PropertyModel2, self).data(index, role)

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled

        return super(PropertyModel2, self).flags(index)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if index.column() == 1:
                index = self.index(index.row(), 0, index)
                item = self.itemFromIndex(index)
                item.set_value(value)
                # noinspection PyUnresolvedReferences
                self.itemChanged.emit(item)
                return True

        return super(PropertyModel2, self).setData(index, value, role)

    def columnCount(self, parent):
        count = super(PropertyModel2, self).columnCount(parent)
        if count > 0:
            return 2
        return count
        # if not parent.isValid():
        #     return 2
        # print(parent, super(PropertyModel2, self).columnCount(parent))
        # return super(PropertyModel2, self).columnCount(parent)




class PropertyModel(QStandardItemModel):
    DEFAULT_VALUE_FOREGROUND_COLOR = QColor(0x80, 0x80, 0x80)

    def __init__(self, parent=None):
        super(PropertyModel, self).__init__(parent)
        self.setHorizontalHeaderLabels(["Property", "Value"])
        self._readonly = False
        self._use_default = False
        self._default_dict = DefaultValues()

    def create_filter_model(self, property_filter, parent=None):
        return PropertyFilterModel(self, property_filter, parent)

    def create_property(self, key, params, label_name=None):
        # type: (string_types, dict, string_types or None) -> PropertyItem
        label_name = label_name or params.get("label") or key
        value = params.get("value")
        default_value = self.default_value(key) or params.get("default")

        item = PropertyItem(key, label_name, value, params, default_value)

        # if "default" in params:
        #     self._model.set_default_value(key, params["default"], update=False)

        item.update_link(self.default_value(key))
        item.set_required(params.get("required", False))

        if params.get("description"):
            html = self._html(params.get("description").strip(), label_name, "###")
            item.setToolTip(html)

        return item

    def _load_settings(self, settings, params_dict):
        key_item_map = {}

        for setting in settings:
            if isinstance(setting, string_types):
                if "#" == setting[0]:
                    self.add_category(setting, setting[1:].strip())
                    continue
                else:
                    key = setting
                    params = params_dict.get(setting, {})
            elif isinstance(setting, dict):
                key = list(setting.keys())[0]
                params = params_dict.get(key, {}).copy()
                params.update(setting[key])
            else:
                raise ValueError(setting)

            item = self.create_property(key, params)
            self.add_property_item(item)
            key_item_map[key] = [item, params]

        return key_item_map

    def load_settings(self, settings, params_dict=None):
        # (dict) -> None
        params_dict = params_dict or {}

        key_item_map = self._load_settings(settings, params_dict)

        # setup link
        prop_map = self.property_map()
        for key, (item, params) in key_item_map.items():
            if "link" not in params:
                continue
            item = prop_map[key]
            item.set_link(prop_map.get(params["link"]))

    def properties(self):
        # type: () -> Iterator[PropertyItem]
        for row in range(self.rowCount()):
            item = self.item(row)
            if item.type() == PropertyItemType:
                yield item

    def property_map(self):
        # type: () -> Dict[string_types, PropertyItem]
        prop_map = OrderedDict()
        for item in self.properties():
            prop_map[item.key] = item
        return prop_map

    def set_default_dict(self, default_dict):
        # (dict) -> None
        if isinstance(default_dict, DefaultValues):
            self._default_dict = default_dict
        elif isinstance(default_dict, dict):
            self._default_dict = DefaultValues(default_dict)
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
        self._default_dict.set_default_value(key, value)

    def add_category(self, key, name):
        # type: (string_types, string_types) -> CategoryItem
        item = CategoryItem(key, name)
        self.add_category_item(item)
        return item

    def add_category_item(self, item):
        # type: (CategoryItem) -> None
        self.appendRow(item)

    def add_property_item(self, item):
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

    @staticmethod
    def _html(dec, title, title_prefix="#"):
        md = """
    {title_prefix} {title}
    {}
            """.strip().format(dec, title=title, title_prefix=title_prefix)

        mdo = markdown.Markdown(extensions=["gfm"])
        return mdo.convert(md)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 1:
                item = self._property_item(index)
                if item:
                    value = item.value
                    if value is None:
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
                index = self.index(index.row(), 0, index.parent())
                item = self.itemFromIndex(index)
                item.set_value(value)
                # noinspection PyUnresolvedReferences
                self.itemChanged.emit(item)
                return True

        return super(PropertyModel, self).setData(index, value, role)


class BaseItem(QStandardItem):
    def tree_key(self):
        keys = []
        item = self
        while item:
            keys.append(item.key)
            item = item.parent()

        return tuple(reversed(keys))

    def add_property(self, *args, **kwargs):
        self.model().add_property(self, *args, **kwargs)


class CategoryItem(BaseItem):
    is_category = True
    BACKGROUND_COLOR = QColor(71, 74, 77)
    FOREGROUND_COLOR = QColor(0xFF, 0xFF, 0xFF)

    @staticmethod
    def type():
        return CategoryItemType

    def __init__(self, key, name):
        # type: (string_types, string_types) -> None
        super(CategoryItem, self).__init__(name)
        self.key = key
        self.setBackground(QBrush(self.BACKGROUND_COLOR))
        self.setForeground(self.FOREGROUND_COLOR)
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setFlags(self.flags() & ~(Qt.ItemIsEditable | Qt.ItemIsSelectable))
        self.setEnabled(True)


class PropertyItem(BaseItem):
    is_category = False
    REQUIRED_FOREGROUND_COLOR = QColor("#f8b862")
    BOLD_FONT = QFont()
    BOLD_FONT.setBold(True)

    @staticmethod
    def type():
        return PropertyItemType

    def __init__(self, key, label, value, params, default_value=None):
        # type: (string_types, dict) -> None
        super(PropertyItem, self).__init__(label)
        self.key = key
        self._value = value
        self.description = params.get("description")
        self.required = params.get("required", False)
        self.require_input = params.get("require_input", False)
        self.link_format = params.get("link_format")

        # value type
        value_type = params.get("value_type")
        if isinstance(value_type, string_types):
            value_type = find_value_type(value_type, params)

        self.value_type = value_type

        # item flags
        self.setFlags(Qt.NoItemFlags)
        self.setEnabled(True)
        self.setEditable(True)

        # link param
        self.link = None
        self._linked = []

        # default values
        self._default_flag = value is None
        self._default = default_value
        self._default_cache = self._default

        # reserved
        self.validator = None

        self.update_bg_color()

    def update_bg_color(self):
        if not self.is_complete():
            self.setForeground(self.REQUIRED_FOREGROUND_COLOR)
            self.setFont(self.BOLD_FONT)
        else:
            self.setData(None, Qt.ForegroundRole)
            self.setFont(QFont())

    def set_required(self, required):
        self.required = required

    def set_indent(self, indent):
        # type: (int) -> None
        self.setText(("    " * indent) + self.text())

    def set_validator(self, validator):
        # type: (QValidator) -> None
        self.validator = validator

    def set_value(self, value, force_update=False):
        # (Any) -> None
        if value == self._default and not force_update and not self.require_input:
            return

        self._value = self.type_class().filter(value)
        self._default_flag = self.value is None

        for linked in self._linked:
            linked.update_link(value)

        self.update_bg_color()

    def update_link(self, value=None):
        # (Any) -> None
        if self.link is None:
            if self.model():
                self._default = self.model().default_value(self.key) or self._default
                self._default_cache = self._default
                self.update_bg_color()
            return

        link_value = value or self.link.value
        default_value = self.model().default_value(self.key) or self._default

        if self.link_format:
            cache = self.link_format.format(_link_value=link_value, _default_value=default_value)
        elif self.value_type:
            cache = self.value_type.link_value(default_value, link_value)
        else:
            cache = link_value or default_value

        self.type_class().set_link(link_value)
        self._default_cache = self.type_class().filter(cache)
        self.update_bg_color()

    @property
    def value(self):
        # type: () -> any
        if self._value is not None:
            return self._value
        else:
            return self._default_cache

    def was_default(self):
        # type: () -> bool
        return self._default_flag

    def set_link(self, link):
        # type: (PropertyItem or None) -> None
        if link is None:
            return

        self.link = link
        # noinspection PyProtectedMember
        link._linked.append(self)
        self.update_link(link.value)

    def set_link_value(self, value):
        link = ValueItem(value)
        self.set_link(link)

    def is_complete(self):
        # type: () -> bool
        if self.required:
            if not self.value:
                return False

            if not self._value and self.require_input:
                return False

        return True

    def type_class(self):
        return self.value_type or TypeBase


