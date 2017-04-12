#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import yaml
from PySide.QtGui import *
from .util.exec_sphinx import launch
from typing import Iterator
from six import string_types

Editors = {}


def init():
    # type: () -> None
    global Editors
    Editors = {}


def load_plugin(file_name):
    # type: (string_types) -> None
    global Editors

    root = os.path.dirname(file_name)
    ext_name = os.path.basename(file_name)[:-len(".yaml")]
    setting_dict = yaml.load(open(file_name))
    Editors[ext_name] = Editor(root, ext_name, setting_dict)


def get(editor_name=None):
    # type: (string_types) -> Editor
    return Editors.get(editor_name or "vscode")


def editors():
    # type: () -> Iterator[string_types, Editor]
    for name, editor in Editors.items():
        yield name, editor


class Editor(object):
    def __init__(self, root, name, setting_dict):
        # type: (string_types, string_types, dict) -> None
        self._setting_dict = setting_dict
        self._path = setting_dict["path"]
        icon_path = setting_dict.get("icon", os.path.join(root, name + ".png"))
        self.icon = QIcon(icon_path) if os.path.isfile(icon_path) else QIcon()

    @property
    def name(self):
        # type: () -> string_types
        return self._setting_dict["name"]

    def open_dir(self, dir_path):
        # type: (string_types) -> None
        if "open_dir" not in self._setting_dict:
            return

        param = self._setting_dict["open_dir"]["param"]
        cmd = param.format(**self._setting_dict)
        launch(cmd, dir_path)
