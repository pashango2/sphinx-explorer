#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
from PySide.QtGui import *
from PySide.QtCore import *
from .sphinx_analyzer import SphinxInfo


class ProjectListModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(ProjectListModel, self).__init__(parent)

        self.setHorizontalHeaderLabels([
            "Document Path",
        ])

    def load(self, project_list):
        # type: ([str]) -> None
        for project_name in project_list:
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
        item = ProjectItem(project_path)
        return item


class ProjectItem(QStandardItem):
    def __init__(self, name):
        super(ProjectItem, self).__init__(name)
        self.info = SphinxInfo(name)

        dir_path, base_name = os.path.split(self.info.conf_py_path)

        from sphinx.config import Config
        from sphinx.util.tags import Tags
        print(dir_path, base_name)
        tags = Tags(None)
        self.config = Config(dir_path, base_name, {}, tags)

        def warn(x):
            pass

        self.config.check_unicode(warn)
        # defer checking types until i18n has been initialized

        # initialize some limited config variables before initialize i18n and loading
        # extensions
        self.config.pre_init_values(warn)
        self.config.init_values(warn)


        print(self.config.project)