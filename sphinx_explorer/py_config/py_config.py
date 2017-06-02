#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import codecs
import yaml
from string import Formatter
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
    def from_yaml_string(yaml_string, values_dict=None, params_dict=None, parent=None):
        """
        load from yaml file.

        :type values_dict: dict or None
        :param string_types yaml_string: yaml string
        :param QWidget parent: parent widget
        :rtype: Config
        """
        return ConfigModel(yaml.load(yaml_string), values_dict, params_dict, parent)

    def __init__(self, config, values_dict=None, params_dict=None, parent=None):
        super(ConfigModel, self).__init__(parent)
        self._item_dict = {}
        self.load(config, values_dict, params_dict)

    def load(self, config, values_dict=None, params_dict=None):
        self.clear()
        self._item_dict = {}
        params_dict = params_dict or {}
        values_dict = values_dict or {}
        root_item = self.invisibleRootItem()

        def _load(_root_item, _config, _parent_key):
            _last_item = None
            _last_key = None
            for x in _config:
                _key = None
                value = None
                if isinstance(x, string_types):
                    _key, value = x, params_dict.get(x, {})
                elif isinstance(x, dict):
                    for _key, value in x.items():
                        break
                elif isinstance(x, (list, tuple)):
                    assert _last_key is not None
                    _load(_last_item, x, _parent_key + _last_key)
                    continue
                else:
                    continue

                value = value or {}

                g = self.PrefixRe.match(_key)
                _category_flag = False
                # header_flag = False
                # vbox_flag = False
                if g:
                    prefix, _key = g.group(1), g.group(2)
                    _category_flag = "#" in prefix
                    # header_flag = "*" in prefix
                    # vbox_flag = "-" in prefix
                    header_level = max(value.get("level", 1), prefix.count("#"))
                    value["header_level"] = value.get("header_level", header_level)

                if _category_flag:
                    _item = CategoryItem(_key, value)
                else:
                    key_path = ".".join(_parent_key + (_key,))
                    _init_value = values_dict.get(key_path)
                    _item = SettingItem(_key, value, _init_value)

                _last_key = _parent_key + (_key,)
                self._item_dict[",".join(_last_key)] = _last_item = _item

                _root_item.appendRow(_item)

        _load(root_item, config, ())

        # setup link
        for _, item in self._item_dict.items():
            if not item.has_link():
                continue
            item.setup_link()

    def get_item(self, key_path):
        key_path = key_path.replace(".", ",")
        return self._item_dict.get(key_path)

    def item_dict(self):
        return self._item_dict

    def get(self, key_path):
        item = self.get_item(key_path)
        if item is None:
            return None

        return item.value

    def set(self, key_path, value):
        item = self.get_item(key_path)
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

    def headers(self, start_index=QModelIndex()):
        groups = []
        group_item = None
        for depth, index in self._index_iter(start_index):
            if depth == 0:
                item = self.itemFromIndex(index)
                yield item

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

    def create_category_tree_proxy_model(self, parent=None):
        """
        Create category-tree-proxy-model.

        :type parent: QWidget
        :rtype: CategoryTreeProxyModel
        """
        model = CategoryTreeProxyModel(parent)
        model.setSourceModel(self)
        return model

    def dump(self, root_index=QModelIndex(), enable_default_value=False):
        """
        Dump as python object.

        :type root_index: QModelIndex
        :type enable_default_value: bool
        :rtype: dict
        """
        obj = {}

        for row in range(self.rowCount(root_index)):
            index = self.index(row, 0, root_index)
            item = self.itemFromIndex(index)
            child_count = self.rowCount(index)

            if child_count > 0:
                _obj = self.dump(index, enable_default_value)
                if _obj:
                    obj[item.key] = _obj
            else:
                if not item.is_category:
                    if item.value is None:
                        continue
                    if item.is_default() and enable_default_value is False:
                        continue

                    obj[item.key] = item.value

        return obj


class BaseItem(QStandardItem):
    """
    Base class of CategoryItem and SettingItem.
    """
    is_category = False

    def __init__(self, name, setting=None):
        """
        :type name: str
        :type setting: dict[str, str]
        """
        setting = setting or {}
        label = setting.get("label", name)
        super(BaseItem, self).__init__(label)
        self.key = name
        self.setting = setting

    def keys(self):
        """
        :rtype: tuple[str]
        """
        keys = [self.key]

        parent = self.parent()
        while parent:
            keys.append(parent.key)
            parent = parent.parent()

        return tuple(reversed(keys))

    def key_path(self, sep="."):
        return sep.join(self.keys())

    def has_link(self):
        return False


class SettingItem(BaseItem):
    LinkParserRe = re.compile("{(.*?)}")

    def __init__(self, name, setting=None, value=None):
        """
        :type name: str
        :type setting: dict[str, str]
        """
        super(SettingItem, self).__init__(name, setting)
        self._default = None
        self._default_format = None
        self._default_elements = None
        self._default_value = None

        if "default" in self.setting:
            default = self.setting["default"]
            if isinstance(default, str):
                elements, fmt = parse_default_format(default)

                if elements:
                    self._default_format = fmt
                    self._default_elements = elements or None

            if self._default_elements is None:
                self._default_value = default

        self._value = value

        # link
        self.linked = []
        self.links = []

        config_type = CONFIG_TYPES.get(setting.get("type", "string"))
        if config_type:
            value_type_class = config_type["class"]
            self.value_type = value_type_class(self, setting)
        else:
            self.value_type = TypeString(self, setting)

        self._display_value = self.value_type.display_value(self.value)

    @property
    def value(self):
        return self._value or self._default_value

    @property
    def default(self):
        if self._default_elements is None:
            return self._default

        model = self.model()
        if model:
            d = {}
            for elm in self._default_elements:
                value = model.get(elm)
                if value is None:
                    keys = self.keys()[:-1] + (elm,)
                    value = model.get(",".join(keys))
                    if value:
                        d[elm] = value
                else:
                    d[elm.replace(".", ",")] = value

            return self._default_format.format_map(d)
        else:
            return None

    def default_value(self):
        model = self.model()
        if model:
            pass
        else:
            return None

    @property
    def display_value(self):
        return self._display_value

    def is_default(self):
        return self._value is None or self._value == self._default

    def set_value(self, value):
        validate_value = self.value_type.validate(value)
        if validate_value is None:
            raise ValueError(value)

        self._value = validate_value
        self._display_value = self.value_type.display_value(self.value)

        if self.linked:
            for link in self.linked:
                link.update_link()

    def control(self, parent):
        return self.value_type.control(parent)

    def has_link(self):
        return bool(self._default_elements)

    def setup_link(self):
        model = self.model()

        for key in self._default_elements:
            item = model.get_item(key)
            if item:
                self.links.append(item)
                item.linked.append(self)

        self.update_link()

    def update_link(self):
        # (Any) -> None
        if self._value is not None or self._default_format is None:
            return

        # create format dict
        self._default_value = self.default

        # self.update_bg_color()


class Map(object):
    def __init__(self, d, key=()):
        self._d = d
        self._key = key

    def __getattr__(self, attr):
        return Map(self._d, self._key + (attr,))

    def __contains__(self, item):
        return item in self._d

    def __str__(self):
        item = self._d.get(".".join(self._key))
        if item is None or item.value is None:
            return ""

        try:
            return str(item.value)
        except AttributeError:
            return ""


def parse_default_format(default):
    fm = Formatter()
    p = fm.parse(default)

    fields = []
    new_default = []
    for literal, field_name, format_spec, conversion in p:
        new_default.append(literal)

        if field_name:
            fields.append(field_name)

            if "." in field_name:
                x = ",".join(field_name.split("."))
                new_default.append("{" + x)
            else:
                new_default.append("{" + field_name)

            if format_spec:
                new_default.append(":" + format_spec)
            if conversion:
                new_default.append("!" + conversion)

            new_default.append("}")

    return fields, "".join(new_default)


class CategoryItem(BaseItem):
    is_category = True

    def __init__(self, name, setting=None):
        """
        :type name: str
        :type setting: dict[str, str]
        """
        super(CategoryItem, self).__init__(name, setting)
        self.header_level = self.setting.get("header_level", 1)


class CategoryTreeProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().itemFromIndex(source_index)

        return item and item.is_category and item.header_level == 1

    def itemFromIndex(self, index):
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)

    def columnCount(self, *_):
        return 1

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
