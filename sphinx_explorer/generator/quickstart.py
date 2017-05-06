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


def quickstart_cmd(d, mastertoctree=None):
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
            opts.extend(["-d", key + "=" + quote(value)])
            continue

        if key.startswith("ext-") and key not in arrow_extension:
            continue

        if key in allow_params or key in arrow_extension:
            if isinstance(value, bool):
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

    if mastertoctree:
        cmd += ["-d", "mastertoctree={}".format(mastertoctree)]

    cmd += opts + [d["path"]]

    return commander(cmd)


def apidoc_cmd(d):
    # type: (string_types, string_types, dict) -> string_types
    project_path = d["path"]
    source_dir, _ = get_source_and_build(d)
    source_dir = os.path.join(source_dir, "apidoc")
    source_dir = os.path.abspath(os.path.join(project_path, source_dir))
    module_dir = d["apidoc-sourcedir"]

    if not os.path.isabs(module_dir):
        module_dir = os.path.abspath(os.path.join(project_path, module_dir))

    cmds = [
        "sphinx-apidoc",
        module_dir,
        "-o", source_dir,
        "-e" if d.get("apidoc-separate", False) else "",
        "-P" if d.get("apidoc-private", False) else "",
    ]

    cmds += d.get("pathnames", [])
    return commander(cmds)


def get_source_and_build(d, api_doc=False):
    source_dir = "source" if d.get("sep", False) else "."
    default_build = "_build" if api_doc else "build"
    build_dir = default_build if d.get("sep", False) else "{}build".format(d.get("dot") or "_")

    return source_dir, build_dir


def fix(d, settings, _, apidoc_flag=False):
    source_dir, build_dir = get_source_and_build(d)
    project_path = d["path"]
    conf_py_path = os.path.abspath(os.path.join(d["path"], source_dir, "conf.py"))

    if apidoc_flag:
        module_dir = d["apidoc-sourcedir"]

        if os.path.isabs(module_dir):
            conf_py_dir = os.path.dirname(conf_py_path)
            try:
                module_dir = os.path.relpath(module_dir, conf_py_dir)
            except ValueError:
                module_dir = os.path.abspath(module_dir)

        apidoc_dict = ProjectSettings.create_apidoc_dict(
            module_dir,
            d.get("apidoc-separate", False),
            d.get("apidoc-private", False)
        )
    else:
        module_dir = None
        apidoc_dict = None

    ProjectSettings.save(
        project_path,
        source_dir,
        build_dir,
        d.get("project", os.path.basename(project_path)),
        apidoc=apidoc_dict,
    )

    if conf_py_path and os.path.isfile(conf_py_path):
        insert_paths = []

        if apidoc_flag:
            path, b = os.path.split(module_dir)
            if not b:
                path, _ = os.path.split(path)
            insert_paths = [path]

        extend_conf_py(conf_py_path, d, settings, extensions=d, insert_paths=insert_paths)

    return source_dir, build_dir
