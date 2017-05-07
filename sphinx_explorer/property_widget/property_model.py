#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .value_types import find_value_type, TypeBase
from six import string_types
import re
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from .default_value_dict import DefaultValues
from collections import OrderedDict
import markdown

if False:
    from typing import Iterator, Dict, List, Any

__all__ = [
    "PropertyModel",
    "BaseItem",
    "CategoryItem",
    "PropertyItem",
    "ValueItem",
    "FlatTableModel",
]

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1


class PropertyModel(QStandardItemModel):
    PrefixRe = re.compile(r"(^[#*-]*)\s*(.*)")

    def __init__(self, parent=None):
        """
        :param QWidget parent: parent widgets 
        """
        super(PropertyModel, self).__init__(parent)
        self.setHorizontalHeaderLabels([
            self.tr("Property"),
            self.tr("Value")
        ])
        self._default_dict = DefaultValues()
        self._use_default = False
        self.required_flag = True

    def __getattr__(self, key):
        return self.get(key)

    def create_table_model(self, root_index, parent):
        """
        Create table type model.
        
        :param QModelIndex root_index: root index 
        :param QWidget parent: parent widget
        :return: table type model
        :rtype: FlatTableModel
        """
        return FlatTableModel(self, root_index, parent)

    def _load_settings(self, settings, parent_item, params_dict, default_values):
        last_item = None
        for setting in settings:
            if isinstance(setting, dict) and setting:
                key = list(setting.keys())[0]
                setting_param = setting.get(key, [{}])
            elif isinstance(setting, (list, tuple)):
                assert last_item is not None
                self._load_settings(setting, last_item, params_dict, default_values)
                continue
            elif isinstance(setting, string_types):
                key = setting.strip()
                setting_param = {}
            else:
                continue

            if not key:
                continue

            g = self.PrefixRe.match(key)
            category_flag = False
            header_flag = False
            vbox_flag = False
            if g:
                prefix, key = g.group(1), g.group(2)
                category_flag = "#" in prefix
                header_flag = "*" in prefix
                vbox_flag = "-" in prefix

            if category_flag:
                label = setting_param.get("label", key)
                last_item = self.add_category(
                    parent_item, key, label,
                    header_flag, setting_param
                )
                last_item.vbox_flag = vbox_flag
            else:
                _params_dict = params_dict.get(key, {}).copy()
                _params_dict.update(setting_param)

                value = setting_param.get("value")
                default = setting_param.get("default")
                if default is None:
                    default = self._get_default_value(parent_item, key, default_values)
                    if default is None:
                        default = params_dict.get(key, {}).get("default")

                if header_flag:
                    _params_dict["required"] = True
                    _params_dict["require_input"] = True

                last_item = self.add_property(parent_item, key, value, default, _params_dict)

    @staticmethod
    def _get_default_value(parent_item, key, default_values):
        # hierarchy access
        if parent_item and parent_item.index().isValid():
            try:
                d = default_values
                for pkey in parent_item.tree_key():
                    d = d[pkey]
                return d[key]
            except (KeyError, TypeError):
                pass

        # root access
        try:
            return default_values[key]
        except KeyError:
            pass

        return None

    def load_settings(self, settings, params_dict=None, default_values=None):
        root_item = self.invisibleRootItem()
        default_values = default_values or {}
        params_dict = params_dict or {}

        self._load_settings(settings, root_item, params_dict, default_values)

        # setup link
        prop_map = self.property_map()
        for key, item in prop_map.items():
            if "link" not in item.params:
                continue
            item = prop_map[key]
            item.setup_link(prop_map)

    @staticmethod
    def create_category(key, label=None, header_flag=False, params=None):
        # type: (string_types, string_types) -> CategoryItem
        return CategoryItem(key, label or key, header_flag, params)

    @staticmethod
    def create_property(key, value_item, value_type, params=None, label_name=None):
        params = params or {}
        return PropertyItem(
            key,
            label_name or params.get("label", key),
            value_item,
            value_type,
            params
        )

    def add_category(self, parent_item, *args, **kwargs):
        value_item = QStandardItem()
        left_item = self.create_category(*args, **kwargs)
        parent_item.appendRow([left_item, value_item])
        return left_item

    def add_property(self, parent_item, key, value=None, default=None, params=None, label_name=None):
        parent_item = parent_item or self.invisibleRootItem()
        params = params or {}
        value = value if value is not None else params.get("value")
        default = default if default is not None else params.get("default")
        label_name = label_name or params.get("label") or key

        # value type
        value_type = params.get("value_type")
        if isinstance(value_type, string_types):
            value_type = find_value_type(value_type, params)

        value_item = ValueItem(value, default, value_type)
        left_item = self.create_property(key, value_item, value_type, params, label_name)

        if params.get("description"):
            html = self._html(params.get("description").strip(), label_name, "###")
            left_item.setToolTip(html)

        parent_item.appendRow([left_item, value_item])
        left_item.check_enable()
        return left_item

    def rowItem(self, index):
        # type: (QModelIndex) -> PropertyItem
        index = self.index(index.row(), 0, index.parent()) if index.column() != 0 else index
        item = self.itemFromIndex(index)  # type: PropertyItem
        return item

    def _property_item(self, index):
        # type: (QModelIndex) -> PropertyItem or None
        if not index.isValid():
            return None

        item = self.itemFromIndex(self.index(index.row(), 0, index.parent()))
        if item.type() == PropertyItemType:
            return item
        return None

    def get(self, keys, root_index=QModelIndex()):
        if isinstance(keys, string_types):
            keys = keys.split(".")

        parent = self.itemFromIndex(root_index) if root_index.isValid() else self.invisibleRootItem()
        for key in keys:
            for row in range(parent.rowCount()):
                item = parent.child(row)  # type: PropertyItem
                if item.key == key:
                    parent = item
                    break
            else:
                return None

        return parent

    def set_values(self, values, root=None):
        root = root or self.invisibleRootItem()
        values = values or {}
        for property_item in self.properties(root.index()):
            value = self._get_default_value(property_item.parent(), property_item.key, values)
            property_item.set_value(value)

    def properties(self, root_index=None):
        # type: () -> Iterator[PropertyItem]
        root_index = root_index or QModelIndex()
        for index in self.model_iter(root_index, False):
            item = self.itemFromIndex(index)
            if item and item.type() == PropertyItemType:
                yield item

    def headers(self, root=None):
        # type: () -> Iterator[PropertyItem]
        root = root or QModelIndex()
        for index in self.model_iter(root, False):
            item = self.itemFromIndex(index)  # type: BaseItem
            if item.header_flag:
                yield item

    def property_map(self):
        # type: () -> Dict[string_types, PropertyItem]
        prop_map = OrderedDict()
        for item in self.properties():
            prop_map[item.key] = item
        return prop_map

    def is_complete(self, root_index=QModelIndex()):
        # type: () -> bool
        for property_item in self.properties(root_index):
            if not property_item.is_complete():
                return False
        return True

    @staticmethod
    def _html(markdown_str, title, title_prefix="#"):
        md = """
{title_prefix} {title}
{}
        """.strip().format(markdown_str, title=title, title_prefix=title_prefix)

        mdo = markdown.Markdown(extensions=["gfm"])
        return mdo.convert(md)

    def model_iter(self, parent_index=QModelIndex(), col_iter=True):
        """
        :rtype: generator(QModelIndex)
        :type col_iter: bool
        :type parent_index: QModelIndex
        """
        index = self.index(0, 0, parent_index)
        if not index.isValid():
            return

        while True:
            if col_iter:
                for col in range(0, self.columnCount(parent_index)):
                    yield index.siblding(index.row(), col)
            else:
                yield index

            if self.rowCount(index) > 0:
                for _ in self.model_iter(index, col_iter):
                    yield _

            index = index.sibling(index.row() + 1, index.column())
            if not index.isValid():
                break

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.ToolTipRole:
            if index.column() == 1:
                index = index.sibling(index.row(), 0)
                return index.data(role)

        return super(PropertyModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        # type: (QModelIndex, Any, int) -> bool
        if role == Qt.CheckStateRole:
            checked = value == Qt.Checked
            item = self.itemFromIndex(index)

            ch_item = item.child(0, 0)
            ch_item.setEnabled(checked)
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(ch_item.index(), ch_item.index())
        elif role == Qt.EditRole:
            item = self.rowItem(index)
            item.set_value(value)
            return True

        return super(PropertyModel, self).setData(index, value, role)

    def dump(self, store_none=False, flat=False, exclude_default=False):
        # type: (bool, bool, bool) -> dict
        dump_dict = OrderedDict()

        for index in self.model_iter(col_iter=False):
            item = self.itemFromIndex(index)
            key = item.tree_key()

            if item.is_category:
                continue

            if item.value is not None:
                if exclude_default and item.was_default():
                    continue
            else:
                if store_none is False:
                    continue

            dump_dict[key] = item.value

        result_dict = {}
        if flat:
            for key, value in dump_dict.items():
                result_dict[key[-1]] = value
        else:
            for key, value in dump_dict.items():
                parent_key, key = key[:-1], key[-1]
                parent_dict = result_dict

                if parent_key:
                    for k in parent_key:
                        if k not in parent_dict:
                            parent_dict[k] = {}
                        parent_dict = parent_dict[k]
                parent_dict[key] = value

        return result_dict


class BaseItem(QStandardItem):
    is_category = True

    def __init__(self, key, name):
        # type: (string_types, string_types) -> None
        super(BaseItem, self).__init__(name)
        self.key = key
        self.header_flag = False
        self.vbox_flag = False

    def __getattr__(self, item):
        for row in range(self.rowCount()):
            ch_item = self.child(row, 0)
            if ch_item.key == item:
                return ch_item
        raise AttributeError(item)

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

    def set_values(self, values, root=None):
        return self.model().set_values(values, root or self)

    def enabled(self):
        if not self.isCheckable():
            return True
        return self.checkState() == Qt.Checked

    def check_enable(self):
        parent = self.parent()
        while parent:
            if parent.isCheckable():
                self.setEnabled(parent.checkState() == Qt.Checked)
            parent = parent.parent()

    def setChecked(self, checked):
        if checked:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

    def update_enabled(self, parent_check, checked_parent):
        if self is not checked_parent:
            if parent_check != self.isEnabled():
                self.setEnabled(parent_check)
                if self.model():
                    self.model().dataChanged.emit(self.index(), self.index())

        for row in range(self.rowCount()):
            child = self.child(row, 0)
            child.update_enabled(parent_check, checked_parent)


class CategoryItem(BaseItem):
    BACKGROUND_COLOR = QColor(71, 74, 77)
    FOREGROUND_COLOR = QColor(0xFF, 0xFF, 0xFF)

    def type(self):
        return CategoryItemType

    def __init__(self, key, name, header_flag, params=None):
        # type: (string_types, string_types, bool, dict) -> None
        super(CategoryItem, self).__init__(key, name)
        self.setBackground(QBrush(self.BACKGROUND_COLOR))
        self.setForeground(self.FOREGROUND_COLOR)
        self.header_flag = header_flag
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setFlags(self.flags() & ~(Qt.ItemIsEditable | Qt.ItemIsSelectable))
        self.setEnabled(True)

        params = params or {}
        checkable = params.get("checkable", False)
        if checkable:
            checked = params.get("default", False)
            self.setCheckable(True)
            self.setCheckState(Qt.Checked if checked else Qt.Unchecked)


class PropertyItem(BaseItem):
    is_category = False
    REQUIRED_FOREGROUND_COLOR = QColor("#f8b862")
    BOLD_FONT = QFont()
    BOLD_FONT.setBold(True)

    LinkParserRe = re.compile("{(.*?)}")

    def __init__(self, key, label, value_item, value_type, params):
        # type: (string_types, dict) -> None
        super(PropertyItem, self).__init__(key, label)
        self.value_item = value_item
        self.description = params.get("description")
        self.description_path = params.get("description_path", ".")
        self.required = params.get("required", False)
        self.require_input = params.get("require_input", False)
        self.replace_space = params.get("replace_space")
        value_item.allow_empty = params.get("allow_empty", True)
        self.params = params

        # value type
        self.value_type = value_type

        # item flags
        self.setFlags(Qt.NoItemFlags)
        self.setEnabled(True)
        self.setEditable(False)

        # link param
        self.link = None
        self._linked = []
        self._links = []

        # default values
        self._default_flag = value_item.value is None

        # reserved
        self.validator = None

        self.update_bg_color()

    @staticmethod
    def parse_link(link):
        # type: (string_types) -> List[string_types]
        return PropertyItem.LinkParserRe.findall(link)

    def type(self):
        return PropertyItemType

    @property
    def default(self):
        return self.value_item.default

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

    def set_value(self, value, force_update=False, not_set_value=False):
        # (Any) -> None
        if not not_set_value:
            # noinspection PyUnreachableCode
            self.value_item.set_value(self.type_class().filter(value))

        self._default_flag = self.value is None

        for linked in self._linked:
            linked.update_link()

        self.update_bg_color()

    def update_link(self):
        # (Any) -> None
        if self.link is None:
            if self.model():
                self.value_item.set_default_display(self.default)
                self.update_bg_color()
            return

        # create format dict
        default_value = self.value_item.default

        if self.link:
            d = {
                "_default": default_value,
            }
            for item in self._links:
                value = item.value if item.value else ""
                if self.replace_space is not None:
                    value = value.replace(" ", self.replace_space)
                    value = value.replace("　", self.replace_space)
                d[item.key] = value

            try:
                cache = self.link.format(**d)
            except KeyError:
                cache = default_value
        else:
            cache = default_value

        # self.type_class().set_link(link_value)
        self.value_item.set_default_display(self.type_class().filter(cache))
        self.update_bg_color()

    @property
    def value(self):
        # type: () -> any
        return self.value_item.value

    def was_default(self):
        # type: () -> bool
        return self.value_item.was_default()

    def setup_link(self, prop_map):
        # type: (dict, string_types) -> None
        link = self.params.get("link")
        if not link:
            return

        self._links = []

        keys = self.parse_link(link)
        if not keys:
            keys = [link]
            link = "{" + link + "}"

        for key in keys:
            item = prop_map.get(key)
            if item:
                self._links.append(item)
                # noinspection PyProtectedMember
                item._linked.append(self)

        self.link = link
        self.update_link()

    def is_complete(self):
        # type: () -> bool
        if self.required and self.model() and self.model().required_flag:
            if not self.value:
                return False

            if not self.value_item.input_value and self.require_input:
                return False

        return True

    def type_class(self):
        return self.value_type or TypeBase


class ValueItem(QStandardItem):
    DEFAULT_VALUE_FOREGROUND_COLOR = QColor(0x80, 0x80, 0x80)

    def __init__(self, value, default, value_type):
        super(ValueItem, self).__init__()
        self._input_value = value
        self._default_value = default
        self._default_display = default
        self.value_type = value_type
        self.setFlags(self.flags() | Qt.ItemIsEditable | Qt.ItemIsSelectable)
        self.allow_empty = True

        self.set_value(value)
        if self.value_type:
            self.setSizeHint(self.value_type.sizeHint())
            self.value_type.setup(self)

    @property
    def input_value(self):
        return self._input_value

    @property
    def value(self):
        if not (not (self._input_value is None) and not (not (self._input_value or self.allow_empty))):
            return self._default_display
        # noinspection PyUnreachableCode
        return self._input_value

    def was_input(self):
        return self._input_value is None

    def was_default(self):
        return self._input_value is None or self._input_value == self._default_value

    @property
    def default(self):
        return self._default_value

    def set_default_display(self, value):
        self._default_display = value
        if not self._input_value:
            self.set_value(self._input_value)

    def update(self):
        if not self._input_value:
            self.set_value(self._input_value)

    def set_value(self, value):
        _value = value if value is not None else self._default_display
        _value = self.value_type.filter(_value) if self.value_type else _value
        _display_value = self.value_type.data(_value) if self.value_type else _value

        if isinstance(_display_value, bool):
            _display_value = "Yes" if _display_value else "No"

        self.setText(_display_value or "")
        self._input_value = value

        icon = self.value_type.icon(_value) if self.value_type else None
        if icon:
            self.setIcon(icon)

        if value is not None:
            self.setData(None, Qt.ForegroundRole)
        else:
            self.setForeground(self.DEFAULT_VALUE_FOREGROUND_COLOR)

        if self.model():
            property_index = self.index().sibling(self.row(), 0)
            property_item = self.model().itemFromIndex(property_index)  # type: PropertyItem
            if property_item:
                property_item.set_value(self.value, not_set_value=True)


class FlatTableModel(QAbstractProxyModel):
    """
    TreeModel -> TableModel Translate Model
    """

    def __init__(self, source_model, root_index, parent=None):
        # type: (PropertyModel, QModelIndex, QWidget) -> None
        super(FlatTableModel, self).__init__(parent)
        self._map_dict = {}
        self._from_dict = {}
        self.row_count = 0

        for i, index in enumerate(source_model.model_iter(root_index, False)):
            self._map_dict[(i, 0)] = index
            self._map_dict[(i, 1)] = index.sibling(index.row(), 1)
            self._from_dict[index] = self.index(i, 0)
            self._from_dict[index.sibling(index.row(), 1)] = self.index(i, 1)
            self.row_count += 1

        self.setSourceModel(source_model)
        # noinspection PyUnresolvedReferences
        source_model.dataChanged.connect(self._onChanged)

    def _onChanged(self, left_index, right_index):
        # noinspection PyUnresolvedReferences
        self.dataChanged.emit(
            self.mapFromSource(left_index),
            self.mapFromSource(right_index)
        )

    # noinspection PyMethodOverriding
    def rowCount(self, index=QModelIndex()):
        if index.isValid():
            return 0
        return self.row_count

    # noinspection PyMethodOverriding
    def columnCount(self, index=QModelIndex()):
        return 2

    # noinspection PyMethodOverriding
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, parent)

    def itemFromIndex(self, index):
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)

    def mapToSource(self, index):
        if not index.isValid():
            return index
        return self._map_dict.get((index.row(), index.column()), QModelIndex())

    def rowItem(self, index):
        return self.sourceModel().rowItem(self.mapToSource(index))

    def mapFromSource(self, source_index):
        if not source_index.isValid():
            return source_index
        try:
            return self._from_dict[source_index]
        except KeyError:
            return QModelIndex()

    def parent(self, index=QModelIndex()):
        return QModelIndex()

    def set_values(self, *args, **kwargs):
        return self.sourceModel().set_values(*args, **kwargs)

    def dump(self, *args, **kwargs):
        return self.sourceModel().dump(*args, **kwargs)
