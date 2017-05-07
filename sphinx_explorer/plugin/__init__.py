#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import fnmatch
# noinspection PyPackageRequirements
import yaml
from qtpy.QtWidgets import *
from typing import Iterator
from six import string_types
from .template_model import TemplateModel
from . import editor
from . import extension

template_model = None


def init(parent=None):
    # type: (QWidget) -> None
    global template_model
    template_model = TemplateModel(parent)
    editor.init()


def load_plugin(sys_dir):
    # type: (string_types) -> None
    global template_model

    # load plugin
    extension.init(os.path.join(sys_dir, "plugin", "extension"))

    editor_dir = os.path.join(sys_dir, "plugin", "editor")
    for file_path in _walk_files(editor_dir, "*.yml"):
        editor.load_plugin(file_path)

    wizard_dir = os.path.join(sys_dir, "plugin", "template")
    for file_path in _walk_files(wizard_dir, "*.yml"):
        template_model.load_plugin(file_path)


def _walk_files(dir_path, ext):
    # type: (string_types, string_types) -> Iterator[string_types]
    order_yml = os.path.join(dir_path, "_order.yml")
    if os.path.isfile(order_yml):
        order = yaml.load(open(order_yml)).get("order", [])
    else:
        order = []

    yaml_dict = {}
    for root, _, files in os.walk(dir_path):
        for file_path in fnmatch.filter(files, ext):
            if file_path[0] != "_":
                ext_name = os.path.splitext(file_path)[0]
                yaml_dict[ext_name] = os.path.join(root, file_path)

    # order sort
    for ext_name in order:
        if ext_name in yaml_dict:
            yield yaml_dict[ext_name]
            del yaml_dict[ext_name]

    for x in yaml_dict.values():
        yield x
