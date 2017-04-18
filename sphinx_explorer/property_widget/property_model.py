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





class PropertyModel2(QStandardItemModel):
    def __init__(self, parent=None):
        super(PropertyModel2, self).__init__(parent)
        self.setHorizontalHeaderLabels(["Property", "Value"])
        self._default_dict = DefaultValues()
        self._use_default = False

    def _load_settings(self, settings, parent_item, params_dict=None):
        params_dict = params_dict or {}

        last_item = None
        for setting in settings:
            if isinstance(setting, dict) and setting:
                key = list(setting.keys())[0]
                setting_param = setting.get(key, [{}])[0]
            elif isinstance(setting, (list, tuple)):
                assert last_item is not None
                self._load_settings(setting, last_item, params_dict)
                continue
            elif isinstance(setting, string_types):
                key = setting.strip()
                setting_param = {}
            else:
                continue

            if not key:
                continue

            if key[0] == "#":
                label = setting_param.get("label", key[1:].strip())
                last_item = self.add_category(parent_item, key, label)
            else:
                d = params_dict.get(key, {}).copy()
                d.update(setting_param)
                last_item = self.add_property(parent_item, key, d)

    def load_settings(self, settings, params_dict=None):
        root_item = self.invisibleRootItem()
        self._load_settings(settings, root_item, params_dict)

        # setup link
        prop_map = self.property_map()
        for key, item in prop_map.items():
            if "link" not in item.params:
                continue
            item = prop_map[key]
            item.set_link(prop_map.get(item.params["link"]))


    @staticmethod
    def create_category(key, label=None):
        # type: (string_types, string_types) -> CategoryItem
        return CategoryItem(key, label or key)

    @staticmethod
    def create_property(key, value_item, params=None, label_name=None):
        params = params or {}
        return PropertyItem(
            key,
            label_name or params.get("label", key),
            value_item,
            params
        )

    def add_category(self, parent_item, *args, **kwargs):
        value_item = QStandardItem()
        left_item = self.create_category(*args, **kwargs)
        parent_item.appendRow([left_item, value_item])
        return left_item

    def add_property(self, parent_item, key, params, label_name=None):
        parent_item = parent_item or self.invisibleRootItem()

        # value type
        value_type = params.get("value_type")
        if isinstance(value_type, string_types):
            value_type = find_value_type(value_type, params)

        value = params.get("value")
        default = self._default_dict.get(key) or params.get("default")
        value_item = ValueItem(value, default, value_type)
        left_item = self.create_property(key, value_item, params, label_name)

        parent_item.appendRow([left_item, value_item])
        return left_item

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

    def default_value(self, key):
        # (string_types) -> any
        return self._default_dict.get(key)

    def set_default_value(self, key, value, update=True):
        # type: (string_types, any, bool) -> None
        if not update and key in self._default_dict:
            return
        self._default_dict.set_default_value(key, value)

    def set_default_dict(self, default_dict):
        # (dict) -> None
        if isinstance(default_dict, DefaultValues):
            self._default_dict = default_dict
        elif isinstance(default_dict, dict):
            self._default_dict = DefaultValues(default_dict)
        self._use_default = bool(default_dict)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            item = self.itemFromIndex(index)
            item.set_value(value)
            return True

        return super(PropertyModel2, self).setData(index, value, role)

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
        return self.model().add_property(self, *args, **kwargs)

    def add_category(self, *args, **kwargs):
        return self.model().add_category(self, *args, **kwargs)





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

    def __init__(self, key, label, value_item, params, default_value=None):
        # type: (string_types, dict) -> None
        super(PropertyItem, self).__init__(label)
        self.key = key
        self.value_item = value_item
        self.description = params.get("description")
        self.required = params.get("required", False)
        self.require_input = params.get("require_input", False)
        self.link_format = params.get("link_format")
        self.params = params

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
        self._default_flag = value_item.value is None
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

        self.value_item.set_value(self.type_class().filter(value))
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
        self.value_item.set_default_value(self.type_class().filter(cache))
        self.update_bg_color()

    @property
    def value(self):
        # type: () -> any
        return self.value_item.value
        # if self._value is not None:
        #     return self._value
        # else:
        #     return self._default_cache

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

            if not self.value_item.input_value() and self.require_input:
                return False

        return True

    def type_class(self):
        return self.value_type or TypeBase


class ValueItem(QStandardItem):
    DEFAULT_VALUE_FOREGROUND_COLOR = QColor(0x80, 0x80, 0x80)

    def __init__(self, value, default, value_type):
        super(ValueItem, self).__init__()
        self._value = None
        self.default = default
        self.value_type = value_type
        self.set_value(value)

    def input_value(self):
        return self._value

    def set_value(self, value):
        _value = value or self.default
        _text = self.value_type.data(_value) if self.value_type else _value
        self.setText(_text)
        self._value = value
        icon = self.value_type.icon(value) if self.value_type else None
        if icon:
            self.setIcon(icon)

        if value:
            self.setData(None, Qt.ForegroundRole)
        else:
            self.setForeground(self.DEFAULT_VALUE_FOREGROUND_COLOR)

    @property
    def value(self):
        return self._value or self.default

    def set_default_value(self, default):
        self.default = default

