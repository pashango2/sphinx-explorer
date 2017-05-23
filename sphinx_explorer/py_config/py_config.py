#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import codecs
import yaml
import re
from six import string_types
from .value_types import *


CONFIG_TYPES = {
    "boolean": {
        "type": bool,
        "class": TypeBool,
    },
    "integer": {
        "type": int,
        "class": TypeInteger,
    },
    "string": {
        "type": str,
        "class": TypeString,
    },
    "array": None,
    # "color": None,
    "object": None,
    "header": None,
    "header_1": None,
    "sub_header": None,
    "header_2": None,
}

CONFIG_TYPES["number"] = CONFIG_TYPES["integer"]


def register_type(type_name, value_class, type_class):
    global CONFIG_TYPES

    CONFIG_TYPES[type_name] = {
        "type": value_class,
        "class": type_class,
    }


class ConfigModel(QStandardItemModel):
    PrefixRe = re.compile(r"(^[#*-]*)\s*(.*)")

    @staticmethod
    def from_yaml(yaml_path, encoding="utf-8", parent=None):
        """
        load from yaml file.

        :param string_types yaml_path: yaml path
        :param string_types encoding: yaml encoding (default: utf-8)
        :param QWidget parent: parent widget
        :rtype: Config
        """
        return ConfigModel(
            yaml.load(codecs.open(yaml_path, "r", encoding=encoding)),
            parent
        )

    @staticmethod
    def from_yaml_string(yaml_string, parent=None):
        """
        load from yaml file.

        :param string_types yaml_string: yaml string
        :param QWidget parent: parent widget
        :rtype: Config
        """
        return ConfigModel(yaml.load(yaml_string), parent)

    def __init__(self, config, parent=None):
        super(ConfigModel, self).__init__(parent)
        self._item_dict = {}
        self.load(config)

    def load(self, config, params_dict=None):
        self.clear()
        self._item_dict = {}
        params_dict = params_dict or {}
        root_item = self.invisibleRootItem()

        def _load(_root_item, _config, _parent_key):
            _last_item = None
            _last_key = None
            for x in _config:
                key = None
                value = None
                if isinstance(x, string_types):
                    key, value = x, params_dict.get(x)
                elif isinstance(x, dict):
                    for key, value in x.items():
                        break
                elif isinstance(x, (list, tuple)):
                    assert _last_key is not None
                    _load(_last_item, x, _parent_key + _last_key)
                    continue
                else:
                    continue

                g = self.PrefixRe.match(key)
                _category_flag = False
                # header_flag = False
                # vbox_flag = False
                if g:
                    prefix, key = g.group(1), g.group(2)
                    _category_flag = "#" in prefix
                    # header_flag = "*" in prefix
                    # vbox_flag = "-" in prefix

                if _category_flag:
                    item = CategoryItem(key)
                else:
                    item = SettingItem(key, value)

                _last_key = _parent_key + (key,)
                self._item_dict[".".join(_last_key)] = _last_item = item

                _root_item.appendRow(item)

        _load(root_item, config, ())

    def get(self, key_path):
        item = self._item_dict.get(key_path)
        if item is None:
            return None

        return item.value

    def set(self, key_path, value):
        item = self._item_dict.get(key_path)
        if item is None:
            return None

        item.set_value(value)

    def _index_iter(self, index, depth=0):
        for row in range(self.rowCount(index)):
            _index = self.index(row, 0, index)
            yield depth, _index

            if self.rowCount(_index) > 0:
                for d, x in self._index_iter(_index, depth + 1):
                    yield d, x

    def config_iter(self, start_index=QModelIndex()):
        for depth, index in self._index_iter(start_index):
            item = self.itemFromIndex(index)
            if item:
                yield depth, item

    def _get_from_keys(self, key_path):
        """
        get config value from key sequence

        :param tuple keys: key sequence
        :rtype: any
        """
        keys = self._parse_key_path(key_path)
        _config = self._config.get("config", {})

        for key in keys:
            if key not in _config:
                raise KeyError()

            _config = _config[key]

        return _config

    @staticmethod
    def _parse_key_path(key_path):
        """
        parse key path

        :param string_types key_path: key path
        :rtype: tuple[string_types]
        """
        if isinstance(key_path, string_types):
            return tuple(key_path.split("."))
        elif isinstance(key_path, (list, tuple)):
            return tuple(key_path)
        else:
            raise ValueError(key_path)

    @Slot(bool)
    def setChecked(self, checked):
        control = self.sender()
        item = control.property("item")
        item.set_value(checked)


class BaseItem(QStandardItem):
    is_category = False

    def key(self):
        keys = [self.text()]

        parent = self.parent()
        while parent:
            keys.append(parent.text())
            parent = parent.parent()

        return tuple(reversed(keys))


class SettingItem(BaseItem):
    def __init__(self, name, setting=None):
        super(SettingItem, self).__init__(name)
        setting = setting or {}
        self.setting = setting
        self._default = setting.get("default")
        self._value = None

        config_type = CONFIG_TYPES.get(setting.get("type", "string"))
        if config_type:
            value_type_class = config_type["class"]
            self.value_type = value_type_class(self, setting)
        else:
            self.value_type = TypeString(self, setting)

        self._display_value = self.value_type.display_value(self.value)

    @property
    def value(self):
        return self._value or self._default

    @property
    def display_value(self):
        return self._display_value

    def set_value(self, value):
        validate_value = self.value_type.validate(value)
        if validate_value is None:
            raise ValueError(value)

        self._value = validate_value
        self._display_value = self.value_type.display_value(self.value)

    def control(self, parent):
        return self.value_type.control(parent)


class CategoryItem(BaseItem):
    is_category = True


