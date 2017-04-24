#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import toml
import yaml
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from six import string_types

from sphinx_explorer.util import icon
from .util.QConsoleWidget import QConsoleWidget
from .util import python_venv
from .util.conf_py_parser import Parser
from .util.commander import quote, commander
from .property_widget import PropertyWidget, PropertyModel
from .task import push_task
import logging
logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class ProjectListModel(QStandardItemModel):
    projectLoaded = Signal(QModelIndex)
    loadFinished = Signal()

    def __init__(self, parent=None):
        super(ProjectListModel, self).__init__(parent)
        self.setHorizontalHeaderLabels([
            self.tr("Project List"),
        ])

    def load(self, project_list):
        # type: ([str]) -> None
        for project_name in project_list:
            if project_name:
                item = self._create_item(project_name)
                self.appendRow(item)

    def dump(self):
        # type: () -> [str]
        items = [self.itemFromRow(row) for row in range(self.rowCount())]
        return [item.path() for item in items]

    def itemFromRow(self, row):
        # type: (int) -> ProjectItem
        return self.item(row, 0)

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
            item = self.itemFromIndex(index)
            if item.path() == doc_path:
                return index
        return QModelIndex()

    def itemFromIndex(self, index):
        # type: (QModelIndex) -> ProjectItem
        index = self.index(index.row(), 0)
        item = super(ProjectListModel, self).itemFromIndex(index)   # type: ProjectItem
        return item

    def _create_item(self, project_path):
        # type: (str) -> QStandardItem
        item = ProjectItem("-", os.path.normpath(project_path))
        item.setIcon(icon.load("eye"))

        self._analyze_item(item)

        return item

    def update_items(self):
        for row in range(self.rowCount()):
            item = self.item(row, 0)    # type: ProjectItem
            self._analyze_item(item)

    def _analyze_item(self, item):
        project_path = item.path()

        ana = LoadSettingObject(project_path, item.path())
        # noinspection PyUnresolvedReferences
        ana.finished.connect(self.onAnalyzeFinished)

        # noinspection PyArgumentList
        push_task(ana)

    @Slot(object, str)
    def onAnalyzeFinished(self, settings, project_path):
        # type: (ProjectSettings, str, str) -> None
        index = self.find(project_path)
        if not index.isValid():
            return

        item = self.itemFromIndex(index)
        item.setInfo(settings)
        if settings.is_valid():
            item.setIcon(icon.load("book"))
            self.projectLoaded.emit(item.index())
        else:
            item.setIcon(icon.load("error"))
            logger.error(settings.error_msg)

        if settings.project:
            item.setText("{} ({})".format(settings.project, project_path))
        else:
            item.setText(project_path)

        if item.model():
            _left = item.index()                        # QModelIndex
            _right = item.model().index(_left.row(), 1)
            # noinspection PyUnresolvedReferences
            item.model().dataChanged.emit(_left, _right)

    def path(self, index):
        # type: (QModelIndex) -> str
        item = self.item(index.row(), 0)    # type: ProjectItem
        return item and item.path()

    def rowItem(self, index):
        # type: (QModelIndex) -> ProjectItem
        index = self.index(index.row(), 0) if index.column() != 0 else index
        return self.itemFromIndex(index)


class ProjectItem(QStandardItem):
    def __init__(self, name, path):
        super(ProjectItem, self).__init__(name)
        self.settings = ProjectSettings(path)    # type: ProjectSettings
        self._path = path
        self._tools = None

    def set_tools(self, tools):
        self._tools = tools

    def project(self):
        return self.settings.project

    def path(self):
        # type: () -> string_types
        return self._path

    def source_dir_path(self):
        # type: () -> string_types
        try:
            return os.path.join(self._path, self.settings.source_dir)
        except (ValueError, TypeError):
            return self._path

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
            cmd = "sphinx-autobuild -p 0 -s 1 --open-browser {} {}".format(
                quote(self.settings.source_dir),
                quote(os.path.join(self.settings.build_dir, target)),
            )
            return cmd
        return None

    def apidoc_update(self, output_widget):
        # type: (QConsoleWidget) -> None
        module_dir = self.settings.module_dir
        if not module_dir or not self.settings.source_dir:
            return

        project_dir = self.path()
        source_dir = os.path.join(project_dir, self.settings.source_dir)
        module_dir = os.path.join(source_dir, module_dir)
        cmd = self.api_update_cmd(
            module_dir,
            source_dir,
            {}
        )

        output_widget.exec_command(cmd, cwd=self.settings.source_dir)

    @staticmethod
    def api_update_cmd(source_dir, output_dir, settings):
        # type: (string_types, string_types, dict, string_types or None) -> int
        command = [
                      "sphinx-apidoc",
                      source_dir,
                      "-o", output_dir,
                      # "-e" if settings.get("separate", True) else "",
                      "-f",
                  ] + settings.get("pathnames", [])

        return commander(command)

    def setInfo(self, settings):
        # type: (ProjectSettings) -> None
        self.setText(settings.project)
        self.settings = settings

    def can_make(self):
        # type: () -> bool
        return bool(self.settings and self.settings.is_valid())

    def can_apidoc(self):
        # type: () -> bool
        return self.settings.can_apidoc()

    def venv_info(self):
        return self.settings.venv_info()


class ProjectSettings(object):
    SETTING_NAME = "setting.toml"

    def __init__(self, path):
        self.path = path
        self.conf_py_path = None
        self.source_dir = None
        # self.conf = {}
        self.settings = {}
        self.error_msg = ""
        self.project = ""

        self._analyze()

    @staticmethod
    def save(project_path, source_dir, build_dir, project, module_dir=None, cmd=None):
        setting_path = os.path.join(project_path, ProjectSettings.SETTING_NAME)
        setting_obj = ProjectSettings.dump(
            source_dir,
            build_dir,
            project,
            module_dir,
            cmd
        )
        with open(setting_path, "w") as fd:
            toml.dump(setting_obj, fd)

    @staticmethod
    def dump(source_dir, build_dir, project, module_dir=None, cmd=None):
        d = {
            "source_dir": source_dir,
            "build_dir": build_dir,
        }
        if project:
            d["project"] = project
        if cmd:
            d["command"] = cmd

        if module_dir:
            d["apidoc"] = {
                "module_dir": module_dir,
            }
        return d

    def store(self):
        save_path = os.path.join(self.path, self.SETTING_NAME)
        with open(save_path, "w") as fd:
            toml.dump(self.settings, fd)

    def _analyze(self):
        # search conf.py
        self.conf_py_path = self._find_conf_py(self.path)
        self.source_dir = os.path.dirname(self.conf_py_path) if self.conf_py_path else None
        self.settings = {}

        path = os.path.join(self.path, self.SETTING_NAME)
        if os.path.isfile(path):
            try:
                self.settings = toml.load(path)
            except toml.TomlDecodeError as e:
                self.error_msg = "TomlDecodeError: {}".format(e)

        self.project = self.settings.get("project", "-")

    def is_valid(self):
        # type: () -> bool
        return bool(self.conf_py_path and self.settings)

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

    def venv_info(self):
        try:
            env = self.settings["Python Interpreter"].get("python")
            return python_venv.Env.from_str(env)
        except KeyError:
            return None

    def set_python(self, env):
        self.settings.setdefault("Python Interpreter", {})["python"] = env


class LoadSettingObject(QObject):
    finished = Signal(ProjectSettings, str)

    def __init__(self, doc_path, project_path, parent=None):
        # type: (str, str) -> None
        super(LoadSettingObject, self).__init__(parent)

        self.doc_path = doc_path
        self.project_path = project_path

    def run(self):
        settings = ProjectSettings(self.doc_path)

        if settings.conf_py_path:
            parser = Parser(settings.conf_py_path)
            settings.project = parser.params().get("project", "")

        self.finished.emit(settings, self.project_path)


ProjectDialogSettings = """
- "#Python Interpreter"
- python:
    - value_type: TypePython
      label: Python Interpreter,
      is_project: true,
"""


# noinspection PyArgumentList
class ProjectSettingDialog(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, project_item, parent=None):
        super(ProjectSettingDialog, self).__init__(parent)
        self.project_item = project_item

        self.layout = QVBoxLayout(self)
        # self.property_widget = PropertyWidget(parent=self)
        self.property_widget = PropertyWidget(self)
        self.model = PropertyModel(self)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )

        self.layout.addWidget(self.property_widget)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)
        self.setWindowTitle(self.tr(str("Project Settings")))
        self.resize(1000, 600)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        settings = yaml.load(ProjectDialogSettings)
        python_dict = settings[1]["python"][0]
        python_dict["project_path"] = project_item.path()
        self.model.load_settings(settings)

        self.property_widget.setModel(self.model)
        self.property_widget.resizeColumnsToContents()

    def accept(self):
        self.property_widget.teardown()
        dump = self.model.dump(flat=True)
        self.project_item.settings.set_python(dump.get("python"))
        self.project_item.settings.store()
        super(ProjectSettingDialog, self).accept()

