#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os

from PySide.QtCore import *
from PySide.QtGui import *

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


class TypeBool(TypeBase):
    @classmethod
    def control(cls, parent):
        combo = QComboBox(parent)
        combo.addItem("Yes")
        combo.addItem("No")
        return combo

    @classmethod
    def set_value(cls, control, value):
        control.setCurrentIndex(0 if value else 1)

    @classmethod
    def value(cls, control):
        return control.currentIndex() == 0

    @staticmethod
    def data(value):
        return "Yes" if value else "No"


class TypeDirPath(TypeBase):
    @classmethod
    def control(cls, parent):
        return PathParamWidget(parent)

    @classmethod
    def set_value(cls, control, value):
        control.setText(value)

    @classmethod
    def value(cls, control):
        return control.text()


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

    def add_property(self, label_name, value, value_type=None):
        # type: (str, any, any) -> PropertyItem
        item = PropertyItem(label_name, value, value_type)
        self._model.add_property(item)

        height = item.sizeHint().height()
        if height > 0:
            self.setRowHeight(item.row(), height)

        return item

    def setReadOnly(self, readonly):
        # type: (bool) -> None
        self._model.setReadOnly(readonly)


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
        if role == Qt.DisplayRole:
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

        self.setBackground(QBrush(QColor(0, 0, 0xFF)))
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)


class PropertyItem(QStandardItem):
    @staticmethod
    def type():
        return PropertyItemType

    def __init__(self, label, value, value_type=None):
        # type: (str, any, int) -> None
        super(PropertyItem, self).__init__(label)
        self.value = value
        self.value_type = value_type
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)


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
        model = index.model()           # :type: PropertyModel
        item = model.rowItem(index)     # :type: PropertyItem

        if item.value_type:
            item.value_type.set_value(editor, item.value)
        else:
            super(PropertyItemDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        # type: (QWidget, PropertyModel, QModelIndex) -> None
        model = index.model()           # :type: PropertyModel
        item = model.rowItem(index)     # :type: PropertyItem

        if item.value_type is None:
            super(PropertyItemDelegate, self).setModelData(editor, model, index)
        else:
            value = item.value_type.value(editor)
            model.setData(index, value, Qt.EditRole)


class PathParamWidget(QFrame):
    def __init__(self, parent=None):
        super(PathParamWidget, self).__init__(parent)
        self.line_edit = QLineEdit(self)
        self.ref_button = QToolButton(self)
        self.ref_button.setText("...")
        self.ref_button.setAutoRaise(False)
        self.ref_button.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.ref_button)

        # noinspection PyUnresolvedReferences
        self.ref_button.clicked.connect(self.onRefButtonClicked)

        self.line_edit.setFocusPolicy(Qt.StrongFocus)
        self.ref_button.setFocusPolicy(Qt.NoFocus)
        self.setFocusPolicy(Qt.NoFocus)

        self.line_edit.setFocus()
        self.setFocusProxy(self.line_edit)

    def onRefButtonClicked(self):
        cwd = self.line_edit.text() or os.getcwd()

        # noinspection PyCallByClass
        path_dir = QFileDialog.getExistingDirectory(
            self, "Sphinx root path", cwd
        )
        if path_dir:
            self.line_edit.setText(path_dir)

    def setText(self, text):
        self.line_edit.setText(text)
        self.line_edit.selectAll()
        self.line_edit.setFocus()

    def text(self):
        return self.line_edit.text()


