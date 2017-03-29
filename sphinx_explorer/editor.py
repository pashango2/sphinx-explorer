#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import fnmatch
import toml
from PySide.QtGui import *
from .util.exec_sphinx import launch

Editors = {}


def init(plugin_dir):
    # type: (str) -> None
    global Editors

    Editors = {}
    for root, dirs, files in os.walk(plugin_dir):
        for file_name in fnmatch.filter(files, "*.toml"):
            ext_name = file_name[:-len(".toml")]
            setting_dict = toml.load(os.path.join(root, file_name))
            Editors[ext_name] = Editor(root, ext_name, setting_dict)


def get(ext_name=None):
    # type: (str) -> Editor
    return Editors.get(ext_name or "vscode")


def editors():
    # type: () -> Iterator[str, Editor]
    for name, editor in Editors.items():
        yield name, editor


class Editor(object):
    def __init__(self, root, name, setting_dict):
        # type: (str, str, dict) -> None
        self._setting_dict = setting_dict
        self._path = setting_dict["path"]
        icon_path = setting_dict.get("icon", os.path.join(root, name + ".png"))
        self.icon = QIcon(icon_path) if os.path.isfile(icon_path) else QIcon()

    @property
    def name(self):
        return self._setting_dict["name"]

    def open_dir(self, dir_path):
        # type: (str) -> None
        if "open_dir" not in self._setting_dict:
            return

        param = self._setting_dict["open_dir"]["param"]
        cmd = param.format(**self._setting_dict)
        launch(cmd, dir_path)



