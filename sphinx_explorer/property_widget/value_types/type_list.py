#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *
from .. import define
from .type_base import TypeBase


class BaseListWidget(QListWidget):
    TOOL_WIDTH = 42

    def __init__(self, parent=None):
        super(BaseListWidget, self).__init__(parent)
        self.frame = QFrame(self)
        self.tool_layout = QVBoxLayout(self.frame)
        self.tool_layout.setContentsMargins(0, 0, 0, 0)
        self.tool_layout.setSpacing(0)
        self.tool_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        self.add_act = QAction(define.ADD_ICON, "Add", self, triggered=self._on_add)
        self.up_act = QAction(define.UP_ICON, "Move Up", self, triggered=self.move_up)
        self.up_act.setShortcut("Ctrl+Up")
        self.down_act = QAction(define.DOWN_ICON, "Move Down", self, triggered=self.move_down)
        self.down_act.setShortcut("Ctrl+Down")
        self.del_act = QAction(define.DELETE_ICON, "Delete", self, triggered=self._on_delete)
        self.del_act.setShortcut(QKeySequence.Delete)
        self.actions = [self.add_act, self.up_act, self.down_act, self.del_act]

        for act in self.actions:
            button = QToolButton(self)
            button.setDefaultAction(act)
            button.setAutoRaise(True)
            self.tool_layout.addWidget(button)

            act.setShortcutContext(Qt.WidgetShortcut)
            self.addAction(act)

        self.frame.setLayout(self.tool_layout)

    def input_value(self):
        pass

    def _on_add(self):
        value = self.input_value()
        if value:
            self.addItem(value)

    def _on_delete(self):
        indexes = self.selectedIndexes()
        if indexes:
            indexes.sort(key=lambda x: x.row(), reverse=True)
            for index in indexes:
                self.takeItem(index.row())

    def move_up(self):
        self._move(True)

    def move_down(self):
        self._move(False)

    def _move(self, up_flag):
        # type: (bool) -> None
        indexes = self.selectedIndexes()
        if indexes:
            indexes.sort(key=lambda x: x.row(), reverse=not up_flag)

            selection_model = self.selectionModel()
            selection = QItemSelection()

            stop_idx = -1 if up_flag else self.count()
            first_index = None

            for index in indexes:
                item = self.itemFromIndex(index)
                row = index.row()
                first_index = first_index or index
                if up_flag:
                    insert_row = row - 1
                    movable = stop_idx < insert_row
                else:
                    insert_row = row + 1
                    movable = insert_row < stop_idx

                if movable:
                    self.takeItem(row)
                    self.insertItem(insert_row, item)
                    new_row = insert_row
                else:
                    stop_idx = row
                    new_row = row

                new_index = self.model().index(new_row, 0)
                selection.select(new_index, new_index)

            selection_model.select(
                selection,
                QItemSelectionModel.ClearAndSelect
            )
            selection_model.setCurrentIndex(first_index, QItemSelectionModel.Current)

    def resizeEvent(self, evt):
        width = self.size().width()
        height = self.size().height()

        self.frame.setGeometry(
            width - self.TOOL_WIDTH, 0,
            self.TOOL_WIDTH, height
        )
        return super(BaseListWidget, self).resizeEvent(evt)

    def to_list(self):
        return [
            self.item(row).text()
            for row in range(self.count())
            ]


class FontListWidget(BaseListWidget):
    pass


class DirListWidget(BaseListWidget):
    def input_value(self):
        # noinspection PyCallByClass
        doc_dir = QFileDialog.getExistingDirectory(
            self, "add document", "~",
        )

        return doc_dir


class BaseTypeList(TypeBase):
    WidgetClass = BaseListWidget

    @classmethod
    def control(cls, _, parent):
        return cls.WidgetClass(parent)

    @classmethod
    def value(cls, control):
        return control.to_list()

    @staticmethod
    def data(data):
        if isinstance(data, (list, tuple)):
            return "\n".join(data)
        return data

    @classmethod
    def set_value(cls, control, value):
        # type: (FontListWidget, list) -> None
        control.addItems(value)
        for row in range(control.count()):
            item = control.item(row)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    @classmethod
    def sizeHint(cls):
        return QSize(-1, 180)

    @classmethod
    def setup(cls, item):
        item.setData(Qt.AlignTop | Qt.AlignLeft, Qt.TextAlignmentRole)


class TypeFontList(BaseTypeList):
    WidgetClass = FontListWidget


class TypeDirList(BaseTypeList):
    WidgetClass = DirListWidget
