#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os

from six import string_types

from sphinx_explorer.util.conf_py_parser import extend_conf_py
from sphinx_explorer.util.exec_sphinx import create_cmd, exec_
from sphinx_explorer.project_list_model import ProjectSettings


def create_command(project_path, source_dir, settings=None):
    # type: (string_types, string_types, dict) -> string_types
    settings = settings or {}

    if not os.path.isabs(source_dir):
        source_dir = os.path.abspath(os.path.join(project_path, source_dir))

    cmds = [
        "sphinx-apidoc",
        source_dir,
        "-F",
        "-o", project_path,
        "-e" if settings.get("apidoc-separate", False) else "",
        "-P" if settings.get("apidoc-private", False) else "",
    ]

    if settings.get("project"):
        cmds += ["-H", settings.get("project")]
    if settings.get("author"):
        cmds += ["-A", settings.get("author")]
    if settings.get("version"):
        cmds += ["-V", settings.get("version")]
    if settings.get("release"):
        cmds += ["-R", settings.get("release")]

    cmds += settings.get("pathnames", [])
    return create_cmd(cmds)


def fix_apidoc(project_path, source_dir, params, settings):
    # type: (string_types, string_types, dict, dict) -> None
    if not os.path.isabs(source_dir):
        module_dir = source_dir
    else:
        try:
            module_dir = os.path.relpath(source_dir, project_path)
        except ValueError:
            module_dir = os.path.abspath(source_dir)

    ProjectSettings.save(
        project_path,
        ".", "_build",
        params.get("project"),
        module_dir=module_dir
    )

    conf_py_path = os.path.join(project_path, "conf.py")

    path, b = os.path.split(module_dir)
    if not b:
        path, _ = os.path.split(path)
    extend_conf_py(conf_py_path, params, settings, insert_paths=[path])


def create(project_path, source_dir, settings, cwd=None):
    # type: (string_types, string_types, dict, string_types or None) -> int
    cmd = create_command(project_path, source_dir, settings)

    if not os.path.exists(project_path):
        os.makedirs(project_path)

    return exec_(cmd, cwd)
