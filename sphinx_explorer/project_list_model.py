#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
from PySide.QtCore import *


class ProjectListModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(ProjectListModel, self).__init__(parent)

        self.setHorizontalHeaderLabels([
            "Document Path",
        ])

    def load(self, project_list):
        # type: ([str]) -> None
        for project_name in project_list:
            item = QStandardItem(project_name)
            self.appendRow(item)

    def dump(self):
        # type: () -> [str]
        return [
            self.index(row, 0).data()
            for row in range(self.rowCount())
        ]

    def add_document(self, doc_path):
        # type: (str) -> bool
        if self.find(doc_path).isValid():
            return False

        item = QStandardItem(doc_path)
        self.appendRow(item)

        return True

    def find(self, doc_path):
        # type: (str) -> QModelIndex
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if index.data() == doc_path:
                return index
        return QModelIndex()


