#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from PySide.QtGui import *
from PySide.QtCore import *
from .sphinx_analyzer import SphinxInfo, QSphinxAnalyzer
from . import icon


class ProjectListModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(ProjectListModel, self).__init__(parent)

        self.setHorizontalHeaderLabels([
            "Document Path",
            "Project"
        ])

    def load(self, project_list):
        # type: ([str]) -> None
        for project_name in project_list:
            if project_name and os.path.isdir(project_name):
                item = self._create_item(project_name)
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

        item = self._create_item(doc_path)
        self.appendRow(item)

        return True

    def find(self, doc_path):
        # type: (str) -> QModelIndex
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if index.data() == doc_path:
                return index
        return QModelIndex()

    @staticmethod
    def _create_item(project_path):
        # type: (str) -> QStandardItem
        item = ProjectItem(os.path.normpath(project_path))
        item.setIcon(icon.load("eye"))

        ana = QSphinxAnalyzer(project_path, item)
        ana.finished.connect(ProjectListModel.onAnalyzeFinished)

        # noinspection PyArgumentList
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(ana)

        return item

    @staticmethod
    def onAnalyzeFinished(info, item):
        # type: (SphinxInfo, ProjectItem) -> None
        item.setInfo(info)
        if info.is_valid():
            item.setIcon(icon.load("open_folder"))
        else:
            item.setIcon(icon.load("error"))

        if item.model():
            left = item.index()
            right = item.model().index(left.row(), 1)
            item.model().dataChanged.emit(left, right)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if index.column() == 1:
                index = self.index(index.row(), 0)
                item = self.itemFromIndex(index)
                return item.project()

        return super(ProjectListModel, self).data(index, role)

    def path(self, index):
        # type: (QModelIndex) -> str
        index = self.index(index.row(), 0)
        return index.data()

    def rowItem(self, index):
        # type: (QModelIndex) -> ProjectItem
        index = self.index(index.row(), 0) if index.column() != 0 else index
        return self.itemFromIndex(index)


class ProjectItem(QStandardItem):
    def __init__(self, name):
        super(ProjectItem, self).__init__(name)
        self.info = None

    def setInfo(self, info):
        self.info = info

    def project(self):
        return self.info.conf.get("project") if self.info else None

    def can_make(self):
        # type: () -> bool
        return self.info and self.info.is_valid()
