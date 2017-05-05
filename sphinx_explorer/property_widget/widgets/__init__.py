#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import os
from .. import define


class MovableListWidget(QListWidget):
    TOOL_WIDTH = 42

    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super(MovableListWidget, self).__init__(parent)
        self.frame = QFrame(self)
        self.tool_layout = QVBoxLayout(self.frame)
        self.tool_layout.setContentsMargins(0, 0, 0, 0)
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
        self.input_value_callback = None

    def input_value(self):
        if self.input_value_callback:
            return self.input_value_callback()
        return

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
            width - self.TOOL_WIDTH - 1, 1,
            self.TOOL_WIDTH, height - 2
        )
        return super(MovableListWidget, self).resizeEvent(evt)

    def to_list(self):
        result = [
            self.item(row).text()
            for row in range(self.count())
        ]
        return result or None


class FontListWidget(MovableListWidget):
    pass


# noinspection PyArgumentList
class DirListWidget(MovableListWidget):
    def input_value(self):
        # noinspection PyCallByClass
        doc_dir = QFileDialog.getExistingDirectory(
            self, "add document", os.path.expanduser('~'),
        )

        return doc_dir


# noinspection PyArgumentList
class RefButtonWidget(QFrame):
    def __init__(self, parent=None):
        super(RefButtonWidget, self).__init__(parent)
        self.line_edit = QLineEdit(self)
        self.ref_button = QToolButton(self)
        self.ref_button.setText("...")
        if not define.OPEN_DIR_ICON.isNull():
            self.ref_button.setIcon(define.OPEN_DIR_ICON)

        self.ref_button.setAutoRaise(False)
        self.ref_button.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.ref_button)

        # noinspection PyUnresolvedReferences
        self.ref_button.clicked.connect(self._onRefButtonClicked)
        self.setTabOrder(self.line_edit, self.ref_button)
        self.setFocusProxy(self.line_edit)
        self.setFocusPolicy(Qt.WheelFocus)

        self.line_edit.installEventFilter(self)

        self._block = False

    def eventFilter(self, obj, evt):
        if evt.type() == QEvent.FocusOut:
            if self._block is False:
                # noinspection PyCallByClass
                QApplication.postEvent(self, QFocusEvent(evt.type(), evt.reason()))
                return False
        return super(RefButtonWidget, self).eventFilter(obj, evt)

    def _onRefButtonClicked(self):
        self._block = True
        try:
            self.onRefButtonClicked()
        finally:
            self._block = False

    def setText(self, text):
        self.line_edit.setText(text)
        self.line_edit.selectAll()
        self.line_edit.setFocus()

    def text(self):
        return self.line_edit.text()


class FilePathWidget(RefButtonWidget):
    def __init__(self, _, params=None, parent=None):
        super(FilePathWidget, self).__init__(parent)
        params = params or {}
        self.title = params.get("title", "Open File")
        self.filter = params.get("filter", "All Files (*.*)")
        self.cwd = params.get("cwd")
        self.path = params.get("path")

    def _onRefButtonClicked(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.title,
            self.cwd,
            self.filter
            # "Images (*.png *.jpeg *.jpg *.svg);;All Files (*.*)"
        )
        if filename:
            if self.path:
                filename = os.path.relpath(filename, self.path)
            self.setText(filename)


# noinspection PyArgumentList
class PathParamWidget(RefButtonWidget):
    def __init__(self, delegate, params=None, parent=None):
        super(PathParamWidget, self).__init__(parent)
        params = params or {}
        self.delegate = delegate
        self.title = params.get("selector_title", "Select directory")

    def onRefButtonClicked(self):
        path_dir = self.get_path()
        if path_dir:
            self.setText(path_dir)
            self.closeEditor()

    def closeEditor(self):
        if self.delegate:
            self.delegate.commitData.emit(self)
            self.delegate.closeEditor.emit(self, QAbstractItemDelegate.EditNextItem)

    def get_path(self, cwd=None):
        cwd = cwd or self.line_edit.text() or os.getcwd()
        # noinspection PyCallByClass
        path_dir = QFileDialog.getExistingDirectory(
            self, self.title, cwd
        )
        return path_dir


class RelPathParamWidget(PathParamWidget):
    def __init__(self, delegate, relpath, params=None, parent=None):
        super(RelPathParamWidget, self).__init__(delegate, params, parent)
        self.relpath = relpath

    def onRefButtonClicked(self):
        path_dir = self.get_path(self.relpath)
        if path_dir:
            if self.relpath:
                try:
                    path_dir = os.path.relpath(path_dir, self.relpath)
                    path_dir = path_dir.replace(os.path.sep, "/")
                except ValueError:
                    pass
            self.setText(path_dir)
            self.closeEditor()
