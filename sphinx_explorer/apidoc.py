#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from six import string_types
from .util.exec_sphinx import create_cmd, exec_

DEFAULT_SETTING = {
    "separate": True,
}


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


def create(project_path, source_dir, settings, cwd=None):
    # type: (string_types, string_types, dict, string_types or None) -> int
    cmd = create_command(project_path, source_dir, settings)
    return exec_(create_cmd(cmd), cwd)


def update(source_dir, output_dir, settings, cwd=None):
    # type: (string_types, string_types, dict, string_types or None) -> int
    cmds = [
               "sphinx-apidoc",
               source_dir,
               "-o", output_dir,
               "-e" if settings.get("separate", True) else "",
               "-f",
           ] + settings.get("pathnames", [])
    print(create_cmd(cmds))
    return exec_(create_cmd(cmds), cwd)
