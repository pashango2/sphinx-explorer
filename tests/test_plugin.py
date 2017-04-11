#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import sys
import os


plugin_dir = "plugin"

def test_plugin():
    plugin_text = """
- wizard:
    - Required params
    -
        - project
        - path :
            require_input: false
        - author
        - version
    - Document params
    -
        - language
        - html_theme
        - epub
    - Options
    -
        [
            "sep",
            "prefix",
            "suffix",
            "master",
            "#Build params",
            "makefile",
            "batchfile",
            '#Extensions',
            "ext-autodoc",
            "ext-doctest",
            "ext-intersphinx",
            "ext-todo",
            "ext-coverage",
            "ext-imgmath",
            "ext-mathjax",
            "ext-ifconfig",
            "ext-viewcode",
            "ext-githubpage",
        ]
    - More Extensions
    -
          [
            "ext-commonmark",
            "ext-nbsphinx",
            "ext-fontawesome",
            "ext-blockdiag",
            "ext-autosummary",
        ]
"""
    obj = yaml.load(plugin_text)
    print(obj)

    plugin_text = """
path: atom
name: Atom

open_dir:
    param: "{path} ."
"""
    obj = yaml.load(plugin_text)
    print(obj)






if __name__ == "__main__":
    import pytest
    pytest.main()
