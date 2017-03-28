#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sphinx_explorer.quickstart import cmd
from sphinx_explorer.util.exec_sphinx import exec_
import os

path = os.path.join(
    os.path.dirname(__file__),
    "doc"
)

def test_quickstart():
    d = {'path': '.', 'ext-todo': True, 'batchfile': True, 'ext-mathjax': True, 'mext-fontawesome': True, 'master': 'index',
     'ext-viewcode': True, 'ext-doctest': True, 'ext-imgmath': True, 'language': 'ja', 'mext-nbsphinx': True, 'ext-intersphinx': True,
     'html_theme': 'agogo', 'ext-coverage': True, 'epub': False, 'ext-ifconfig': True, 'suffix': '.rst', 'dot': '_',
     'mext-blockdiag': True, 'ext-autodoc': True, 'makefile': True, 'sep': True, 'ext-githubpage': True}

    opts = []
    for key, value in d.items():
        if key == "path" or not value:
            continue

        if key.startswith("mext-"):
            continue

        if key == "html_theme":
            opts.append("-d " + key + "=" + value)
            continue

        if value is True:
            opts.append("--" + key)
        else:
            opts.append("--" + key + "=" + value)

    exec_(
        " ".join([
            "sphinx-quickstart",
            "-q",
            "-p test",
            "-a author",
            path,
        ] + opts)
    )
