#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from sphinx_explorer.plugin import extension
from sphinx_explorer.generator.quickstart import create_conf_json


def _init_extension():
    plugin_path = os.path.join("..", "sphinx_explorer", "settings", "plugin")
    extension.init(plugin_path)


def test_extension():
    _init_extension()

    options = [
        "ext-fontawesome",
        "ext-pandoc-markdown",
    ]

    ret = create_conf_json(options)
    assert ['sphinx-fontawesome', 'sphinxcontrib-pandoc-markdown'] == ret["packages"]
    assert ["sphinx_fontawesome"] == ret["extensions"]
    assert {'md': 'sphinxcontrib.pandoc_markdown.MarkdownParser'} == ret["source_parser"]


def test_conf_json():
    import importlib

    conf_json = {
        "packages": [
            "sphinxcontrib-mermaid",
            "nbsphinx",
            "sphinx-fontawesome",
            "sphinxcontrib-pandoc-markdown"
        ],
        "extensions": [
            "sphinxcontrib.mermaid",
            "sphinx.ext.graphviz",
            "nbsphinx",
            "sphinx_fontawesome"
        ],
        "source_parser": {
            "md": "sphinxcontrib.pandoc_markdown.MarkdownParser"
        },
        "append_path": []
    }

    globals = {
        "extensions": [],
        "source_parsers": {},
    }

    # extensions
    globals["extensions"] += conf_json.get("extensions", [])

    suffix_list = []
    for ext, parser in conf_json.get("source_parser", {}).items():
        suffix_list.append(ext)
        parser_sp = parser.split(".")

        _module = importlib.import_module(".".join(parser_sp[:-1]))
        globals["source_parsers"][ext] = getattr(_module, parser_sp[-1])

    globals.update(conf_json.get("globals", []))
    print(globals)
