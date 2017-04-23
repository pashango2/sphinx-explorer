#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
from six import string_types

from sphinx_explorer.util.conf_py_parser import extend_conf_py
from sphinx_explorer.util.commander import quote, commander
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

    cmd = [
        "sphinx-quickstart",
        "-q",
        "-p", d["project"],
        "-a", d["author"],
    ]

    if d.get("version"):
        cmd += ["-v", d["version"]]
    if d.get("release"):
        cmd += ["-r", d["release"]]
    cmd += opts + [d["path"]]

    return commander(cmd)


def get_source_and_build(d, api_doc=False):
    source_dir = "source" if d.get("sep", False) else "."
    default_build = "_build" if api_doc else "build"
    build_dir = default_build if d.get("sep", False) else "{}build".format(d.get("dot") or "_")

    return source_dir, build_dir


def fix(d, settings, _):
    source_dir, build_dir = get_source_and_build(d)
    project = d.get("project")
    conf_py_path = os.path.abspath(os.path.join(d["path"], source_dir, "conf.py"))
    project_path = d["path"]

    ProjectSettings.save(project_path, source_dir, build_dir, project)

    if conf_py_path and os.path.isfile(conf_py_path):
        extend_conf_py(conf_py_path, d, settings, extensions=d)
