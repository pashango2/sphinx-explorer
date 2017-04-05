#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from six import string_types
from .util.exec_sphinx import create_cmd, exec_

DEFAULT_SETTING = {
    "separate": True,
}


def create(project_path, module_path):
    pass


def update(source_dir, output_dir, settings, cwd=None):
    # type: (string_types, string_types, dict, string_types or None) -> bool
    cmds = [
        "sphinx-apidoc",
        source_dir,
        "-o", output_dir,
        "-e" if settings.get("separate", True) else "",
        "-f",
    ] + settings.get("pathnames", [])
    print(create_cmd(cmds))
    return exec_(create_cmd(cmds), cwd)
