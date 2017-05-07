#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
# noinspection PyPackageRequirements
import yaml
from qtpy.QtGui import *
from typing import Iterator
from six import string_types
from collections import OrderedDict
from ..util.commander import commander

Editors = OrderedDict()
DEFAULT_EDITOR = "vscode"


def init():
    # type: () -> None
    global Editors
    Editors = OrderedDict()


def load_plugin(file_name):
    # type: (string_types) -> None
    global Editors

    root = os.path.dirname(file_name)
    ext_name = os.path.basename(file_name)[:-len(".yml")]
    setting_dict = yaml.load(open(file_name))
    Editors[ext_name] = Editor(root, ext_name, setting_dict)


def get(editor_name=None):
    # type: (string_types) -> Editor
    return Editors.get(editor_name or "vscode", Editors.get("vscode"))


def default_editor(editor_name=None):
    return editor_name if editor_name in Editors else "vscode"


def check_exist():
    for name, editor in Editors.items():
        if commander.check_exist([editor.path]):
            return name
    return None


def editors():
    # type: () -> Iterator[string_types, Editor]
    for name, editor in Editors.items():
        yield name, editor


class Editor(object):
    def __init__(self, root, name, setting_dict):
        # type: (string_types, string_types, dict) -> None
        self._setting_dict = setting_dict
        self.path = setting_dict["path"]
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
        commander.launch(cmd, dir_path)
