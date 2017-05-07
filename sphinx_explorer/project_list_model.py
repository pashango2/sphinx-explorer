#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import logging
import os

import json
import toml
# noinspection PyPackageRequirements
from qtpy.QtCore import *
from qtpy.QtGui import *
# from qtpy.QtWidgets import *
from six import string_types

from sphinx_explorer import python_venv
from sphinx_explorer.util import icon
from .task import push_task
from .util.commander import commander
logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class ProjectListModel(QStandardItemModel):
    projectLoaded = Signal(QModelIndex)
    loadFinished = Signal()

    def __init__(self, parent=None):
        super(ProjectListModel, self).__init__(parent)

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
        item.setSettings(settings)
        if settings.is_valid():
            item.setIcon(icon.load("book"))
            self.projectLoaded.emit(item.index())
        else:
            item.setIcon(icon.load("error"))
            # logger.error(settings.error_msg)

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
            cmd = [
                "sphinx-autobuild",
                "-p", "0",
                "--delay", "1",
                "--open-browser",
                "--ignore", ".git/*",
                "--ignore", "*.bak",
                "--ignore", "~*.*",
                "--ignore", "___jb_*___",
                self.settings.source_dir,
                os.path.join(self.settings.build_dir, target),
            ]
            return cmd
        return None

    def update_apidoc_command(self):
        # type: () -> (list, string_types)
        module_dir = self.settings.module_dir
        if not module_dir or not self.settings.source_dir:
            return None

        cmd = self.settings.update_apidoc_command(self.path())
        return cmd, self.settings.source_dir

    def setSettings(self, settings):
        # type: (ProjectSettings) -> None
        self.setText(settings.project)
        self.settings = settings

    def can_make(self):
        # type: () -> bool
        return bool(self.settings and self.settings.is_valid())

    def can_apidoc(self):
        # type: () -> bool
        return self.settings.can_apidoc()

    def is_valid(self):
        # type: () -> bool
        return self.settings.is_valid()

    def venv_setting(self):
        return self.settings.venv_setting()


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
    def create_apidoc_dict(module_dir, separate=False, private_member=False, pathnames=None):
        if module_dir is None:
            return None

        d = {"module_dir": module_dir}
        if separate:
            d["separate"] = separate
        if private_member:
            d["private_member"] = private_member
        if pathnames:
            d["pathnames"] = pathnames

        return d

    @staticmethod
    def save(project_path, source_dir, build_dir, project, apidoc=None, cmd=None):
        setting_path = os.path.join(project_path, ProjectSettings.SETTING_NAME)

        setting_obj = {
            "source_dir": source_dir,
            "build_dir": build_dir,
            "project": project,
        }
        if cmd:
            setting_obj["command"] = cmd

        if apidoc:
            setting_obj["apidoc"] = apidoc

        with open(setting_path, "w") as fd:
            toml.dump(setting_obj, fd)

    def store(self):
        save_path = os.path.join(self.path, self.SETTING_NAME)
        with open(save_path, "w") as fd:
            self.settings["project"] = self.project
            toml.dump(self.settings, fd)

        # output conf.json
        conf_path = os.path.join(self.path, self.source_dir, "conf.json")
        with open(conf_path, "w") as fd:
            json.dump(self.conf_json(), fd, indent=4)

    def conf_json(self):
        conf = {}

        epub_settings = self.settings.get("Epub Settings", {})
        if "epub_cover_image" in epub_settings:
            epub_settings["epub_cover"] = (epub_settings["epub_cover_image"], None)
            del epub_settings["epub_cover_image"]

        apidoc_settings = self.settings.get("apidoc", {})

        if "autodoc_default_flags" in apidoc_settings:
            default_flags = []
            for key, value in apidoc_settings["autodoc_default_flags"].items():
                if value:
                    default_flags.append(key)
            if default_flags:
                conf["autodoc_default_flags"] = default_flags

        conf.update(epub_settings)
        return conf

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

    def update_apidoc_command(self, project_dir):
        if not self.module_dir:
            return []

        source_dir = os.path.join(project_dir, self.source_dir)
        module_dir = os.path.join(source_dir, self.module_dir)
        apidoc_dict = self.settings.get("apidoc", {})
        source_dir = os.path.join(source_dir, "apidoc")

        command = [
            "sphinx-apidoc",
            module_dir,
            "-o", source_dir,
            "-e" if apidoc_dict.get("separate", False) else "",
            "-P" if apidoc_dict.get("private_member", False) else "",
        ] + apidoc_dict.get("pathnames", [])

        return commander(command)

    def can_apidoc(self):
        # type: () -> bool
        try:
            return bool(self.settings["apidoc"].get("module_dir"))
        except KeyError:
            return False

    def venv_setting(self):
        try:
            env = self.settings["Python Interpreter"].get("python")
            if env.get("env"):
                return python_venv.VenvSetting(env)
            else:
                return None
        except KeyError:
            return None
        except AttributeError:
            return None

    def set_venv_setting(self, venv_setting):
        self.settings.setdefault("Python Interpreter", {})["python"] = venv_setting

    def update(self, params):
        self.settings.update(params)


class LoadSettingObject(QObject):
    finished = Signal(ProjectSettings, str)

    def __init__(self, doc_path, project_path, parent=None):
        # type: (str, str) -> None
        super(LoadSettingObject, self).__init__(parent)

        self.doc_path = doc_path
        self.project_path = project_path

    def run(self):
        settings = ProjectSettings(self.doc_path)
        self.finished.emit(settings, self.project_path)

