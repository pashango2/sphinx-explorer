#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import codecs
import yaml
import re
from six import string_types
from .value_types import *
from .py_config import ConfigModel
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *


class PropertyView(QTableView):
    def __init__(self, parent=None):
        super(PropertyView, self).__init__(parent)
        self.verticalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.delegate = PropertyItemDelegate(self)

        self.setItemDelegate(self.delegate)

    def setModel(self, model, root_index=QModelIndex()):
        """
        :type model: ConfigModel
        """
        self.clearSpans()

        _model = PropertyTableModel(model, root_index, self)
        super(PropertyView, self).setModel(_model)

        # set category
        for row, item in enumerate(_model.items):
            if item.is_category:
                self.setSpan(row, 0, 1, 2)
            else:
                if item.value_type.is_persistent_editor:
                    index = _model.index(row, 1)
                    self.openPersistentEditor(index)


class PropertyItemDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        model = index.model()   # type: PropertyTableModel
        item = model.itemFromIndex(index)
        control = item.control(parent)
        return control


class PropertyTableModel(QAbstractItemModel):
    def __init__(self, source_model, root_index, parent=None):
        super(PropertyTableModel, self).__init__(parent)
        self.source_model = source_model
        self.root_index = root_index

        self.items = list(item for _, item in source_model.config_iter(root_index))
        self.source_model.dataChanged.connect(self.dataChanged.emit)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, parent)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return [
                    self.tr("Property"),
                    self.tr("Value")
                ][section]

        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.items[index.row()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 1:
                if not item.is_category:
                    if role == Qt.DisplayRole:
                        return item.display_value
                    else:
                        return item.value

        return item.data(role)

    def itemFromIndex(self, index):
        if not index.isValid():
            return None
        return self.items[index.row()]

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            item = self.items[index.row()]
            item.set_value(value)

        return True

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

    def parent(self, index):
        return QModelIndex()
