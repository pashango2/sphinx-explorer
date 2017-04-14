#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import toml
from PySide.QtCore import *
from PySide.QtGui import *
from six import string_types

from sphinx_explorer.generator import apidoc
from . import icon
from .util.QConsoleWidget import QConsoleWidget
from .util.exec_sphinx import quote


class ProjectListModel(QStandardItemModel):
    sphinxInfoLoaded = Signal(QModelIndex)
    autoBuildRequested = Signal(str, QStandardItem)

    def __init__(self, parent=None):
        super(ProjectListModel, self).__init__(parent)

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
        # type: (str) -> QStandardItem or None
        if self.find(doc_path).isValid():
            return None

        item = self._create_item(doc_path)
        self.appendRow(item)

        return item

    def find(self, doc_path):
        # type: (str) -> QModelIndex
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if index.data() == doc_path:
                return index
        return QModelIndex()

    def _create_item(self, project_path):
        # type: (str) -> QStandardItem
        item = ProjectItem(os.path.normpath(project_path))
        item.setIcon(icon.load("eye"))

        self._analyze_item(item)

        return item

    def update_items(self):
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            self._analyze_item(item)

    def _analyze_item(self, item):
        project_path = item.text()

        ana = LoadSettingObject(project_path, item.text())
        ana.finished.connect(self.onAnalyzeFinished)

        # noinspection PyArgumentList
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(ana)

    def onAnalyzeFinished(self, info, project_path):
        # type: (ProjectSettings, str) -> None
        index = self.find(project_path)
        if not index.isValid():
            return

        item = self.itemFromIndex(index)
        item.setInfo(info)
        if info.is_valid():
            item.setIcon(icon.load("book"))
            self.sphinxInfoLoaded.emit(item.index())
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
        self.settings = None    # type: ProjectSettings

    def path(self):
        # type: () -> string_types
        return self.text()

    def html_path(self):
        # type: () -> string_types
        if self.settings.build_dir:
            return os.path.join(
                self.settings.build_dir,
                "html", "index.html"
            )
        return None

    def has_html(self):
        # type: () -> bool
        return bool(self.html_path() and os.path.isfile(self.html_path()))

    def auto_build_command(self, target="html"):
        model = self.model()
        if model:
            cmd = "sphinx-autobuild -p 0 --open-browser {} {}".format(
                quote(self.settings.source_dir),
                quote(os.path.join(self.settings.build_dir, target)),
            )
            return cmd
        return None

    def auto_build(self, target="html"):
        cmd = self.auto_build_command(target)
        model = self.model()
        if model and cmd:
            model.autoBuildRequested.emit(cmd, self)

    def apidoc_update(self, output_widget):
        # type: (QConsoleWidget) -> None
        module_dir = self.settings.module_dir
        if not module_dir or not self.settings.source_dir:
            return

        project_dir = self.text()
        source_dir = os.path.join(project_dir, self.settings.source_dir)
        module_dir = os.path.join(source_dir, module_dir)
        cmd = apidoc.update_cmd(
            module_dir,
            source_dir,
            {}
        )

        output_widget.exec_command(cmd, cwd=self.settings.source_dir)

    def setInfo(self, info):
        # type: (ProjectSettings) -> None
        self.settings = info

    def can_make(self):
        # type: () -> bool
        return bool(self.settings and self.settings.is_valid())

    def can_apidoc(self):
        # type: () -> bool
        return self.settings.can_apidoc()


class ProjectSettings(object):
    SETTING_NAME = "setting.toml"

    def __init__(self, path):
        self.path = path
        self.conf_py_path = None
        self.source_dir = None
        # self.conf = {}
        self.settings = {}

        self._analyze()

    def _analyze(self):
        # search conf.py
        self.conf_py_path = self._find_conf_py(self.path)
        self.source_dir = os.path.dirname(self.conf_py_path) if self.conf_py_path else None
        self.settings = {}

        path = os.path.join(self.path, self.SETTING_NAME)
        if os.path.isfile(path):
            self.settings = toml.load(path)

    def is_valid(self):
        # type: () -> bool
        return bool(self.conf_py_path)

    def can_autobuild(self):
        # type: () -> bool
        return bool(
            self.settings.get("build_dir") and
            self.settings.get("source_dir")
        )

    @staticmethod
    def _find_conf_py(path):
        # type: (str) -> str or None
        assert path

        _path = os.path.join(path, "conf.py")
        if os.path.isfile(_path):
            return _path

        _path = os.path.join(path, "source", "conf.py")
        if os.path.isfile(_path):
            return _path

        return None

    @property
    def auto_build_setting(self):
        return self.settings.get("autobuild", {})

    @property
    def build_dir(self):
        # type: () -> string_types
        try:
            return os.path.join(self.path, self.settings.get("build_dir"))
        except (AttributeError, TypeError):
            return None

    @property
    def module_dir(self):
        # type: () -> string_types
        try:
            return self.settings["apidoc"].get("module_dir")
        except KeyError:
            return ""

    def can_apidoc(self):
        # type: () -> bool
        try:
            return bool(self.settings["apidoc"].get("module_dir"))
        except KeyError:
            return False


class LoadSettingObject(QObject, QRunnable):
    finished = Signal(ProjectSettings, str)

    def __init__(self, doc_path, project_path):
        # type: (str, str) -> None
        QObject.__init__(self)
        QRunnable.__init__(self)

        self.doc_path = doc_path
        self.project_path = project_path

    def run(self):
        info = ProjectSettings(self.doc_path)
        # if info.conf_py_path:
        #     info.read_conf()
        self.finished.emit(info, self.project_path)

