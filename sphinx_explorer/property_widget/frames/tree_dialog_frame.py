#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *

from ..property_model import PropertyModel
from ..property_widget import PropertyWidget


class CategoryFilterModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().itemFromIndex(source_index)

        return item and item.is_category and item.header_flag

    def itemFromIndex(self, index):
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)

    def columnCount(self, *_):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundColorRole:
            return None
        elif role == Qt.ForegroundRole:
            return None

        return super(CategoryFilterModel, self).data(index, role)

    def flags(self, index):
        return (
            Qt.ItemIsSelectable | Qt.ItemIsEnabled

        )


class TreeDialog(QDialog):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super(TreeDialog, self).__init__(parent)
        self.stack_widget_dict = {}

        self.stack_widget = QStackedWidget(self)
        self.tree_view = QTreeView(self)
        self.tree_view.header().hide()

        self.property_widget = PropertyWidget(self)
        self.property_model = PropertyModel(self)

        self.layout = QVBoxLayout()
        self.h_splitter = QSplitter(self)
        self.h_splitter.addWidget(self.tree_view)
        self.h_splitter.addWidget(self.stack_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self
        )
        # noinspection PyUnresolvedReferences
        self.button_box.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.button_box.rejected.connect(self.reject)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.button_box)

        self.layout.addWidget(self.h_splitter)
        self.layout.addLayout(self.h_layout)
        self.setLayout(self.layout)

        # category model
        self.category_model = CategoryFilterModel(self)
        self.category_model.setSourceModel(self.property_model)
        self.tree_view.setModel(self.category_model)
        self.category_selection_model = self.tree_view.selectionModel()

        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setSizes([310, 643])
        self.resize(1000, 600)

        self.category_selection_model.currentChanged.connect(self._on_category_changed)

        self.default_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.property_widget)
        self.default_widget.setLayout(layout)

        self.stack_widget.addWidget(self.default_widget)

    def _on_category_changed(self, current, _):
        item = self.category_model.itemFromIndex(current)
        if item:
            root_item = self.property_model.get(item.tree_key())
            table_model = self.property_model.create_table_model(root_item.index(), self)
            self.property_widget.setModel(table_model)
            self.property_widget.setup()
            self.property_widget.resizeColumnToContents(0)
