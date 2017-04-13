#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import codecs
import os

from six import string_types

from sphinx_explorer.util.conf_py_parser import extend_conf_py
from .util.exec_sphinx import create_cmd, exec_

TEMPLATE_SETTING = """
source_dir = '{rsrcdir}'
build_dir = '{rbuilddir}'

[apidoc]
module_dir = '{module_dir}'
""".strip()


def create_command(project_path, source_dir, settings):
    # type: (string_types, string_types, dict) -> string_types
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
    return " ".join(cmds)


def fix_apidoc(project_path, source_dir, params):
    # type: (string_types, string_types, dict) -> None
    if os.path.abspath(source_dir):
        module_dir = source_dir
    else:
        try:
            module_dir = os.path.relpath(source_dir, project_path)
        except ValueError:
            module_dir = os.path.abspath(source_dir)

    fd = codecs.open(os.path.join(project_path, "setting.toml"), "w", "utf-8")
    fd.write(
        TEMPLATE_SETTING.format(
            rsrcdir=".",
            rbuilddir="_build",
            module_dir=module_dir
        )
    )
    fd.close()

    conf_py_path = os.path.join(project_path, "conf.py")
    extend_conf_py(conf_py_path, params)


def create(project_path, source_dir, settings, cwd=None):
    # type: (string_types, string_types, dict, string_types or None) -> int
    cmd = create_command(project_path, source_dir, settings)

    if not os.path.exists(project_path):
        os.makedirs(project_path)

    return exec_(create_cmd(cmd), cwd)


def update_cmd(source_dir, output_dir, settings):
    # type: (string_types, string_types, dict, string_types or None) -> int
    cmds = [
               "sphinx-apidoc",
               source_dir,
               "-o", output_dir,
               # "-e" if settings.get("separate", True) else "",
               "-f",
           ] + settings.get("pathnames", [])

    return create_cmd(cmds)
