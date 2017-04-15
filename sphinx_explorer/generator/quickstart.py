#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import toml

from six import string_types

from sphinx_explorer.util.conf_py_parser import extend_conf_py
from sphinx_explorer.util.exec_sphinx import quote, command
from ..project_list_model import ProjectSettings

TOML_PATH = "settings/quickstart.toml"
CONF_PY_ENCODING = "utf-8"

TEMPLATE_SETTING = """
source_dir = '{rsrcdir}'
build_dir = '{rbuilddir}'
""".strip()


def quickstart_cmd(d):
    # type: (dict) -> string_types
    ignore_params = ["project", "prefix", "path", "version", "release"]
    arrow_extension = [
        "ext-autodoc",
        "ext-doctest",
        "ext-intersphinx",
        "ext-todo",
        "ext-coverage",
        "ext-imgmath",
        "ext-mathjax",
        "ext-ifconfig",
        "ext-viewcode",
    ]
    allow_params = [
        "suffix", "master", "epub",  "dot", "sep"
    ]

    if "ext-imgmath" in d and "ext-mathjax" in d:
        del d["ext-imgmath"]

    opts = []
    for key, value in d.items():
        if key in ignore_params or not value:
            continue

        if key == "html_theme":
            opts.append("-d " + key + "=" + quote(value))
            continue

        if key.startswith("ext-") and key not in arrow_extension:
            continue

        if key in allow_params:
            if value is True:
                opts.append("--" + key)
            else:
                opts.append("--" + key + "=" + quote(value))

    return command(
        " ".join(
            [
                "sphinx-quickstart",
                "-q",
                "-p " + quote(d["project"]),
                "-a " + quote(d["author"]),
                ("-v " + quote(d["version"])) if d.get("version") else "",
                ("-r " + quote(d["release"])) if d.get("release") else "",
            ] + opts + [quote(d["path"])]
        )
    )


def get_source_and_build(d, api_doc=False):
    source_dir = "source" if d.get("sep", False) else "."
    default_build = "_build" if api_doc else "build"
    build_dir = default_build if d.get("sep", False) else "{}build".format(d.get("dot") or "_")

    return source_dir, build_dir


def fix(d, cmd):
    source_dir, build_dir = get_source_and_build(d)
    conf_py_path = os.path.abspath(os.path.join(d["path"], source_dir, "conf.py"))
    project_path = d["path"]

    setting_obj = ProjectSettings.dump(source_dir, build_dir)
    setting_path = os.path.join(project_path, ProjectSettings.SETTING_NAME)
    with open(setting_path, "w") as fd:
        toml.dump(setting_obj, fd)

    if conf_py_path and os.path.isfile(conf_py_path):
        extend_conf_py(conf_py_path, d, extensions=d)
