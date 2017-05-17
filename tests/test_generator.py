#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from sphinx_explorer.plugin import extension


def _init_extension():
    plugin_path = os.path.join("..", "sphinx_explorer", "settings", "plugin")
    extension.init(plugin_path)


def test_extension():
    _init_extension()

    options = [
        "ext-fontawesome", "ext-pandoc-markdown"
    ]
    ext = extension.get("ext-pandoc-markdown")  # type: extension.Extension

    print(ext.packages)
