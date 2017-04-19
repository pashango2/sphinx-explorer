#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from sphinx_explorer.util import conf_py_parser

here = os.path.abspath(os.path.dirname(__file__))
conf_py_path = os.path.join(here, "conf", "conf.py")


def test_replace():
    parser = conf_py_parser.Parser(conf_py_path)

    replace_dict = {
        "html_theme": str("sphinx_rtd_theme"),
    }
    lines = parser.assign_replace(replace_dict)

    assert lines[84].strip() == "html_theme = 'sphinx_rtd_theme'"


def test_insert_sys_path():
    parser = conf_py_parser.Parser(conf_py_path)
    parser.add_sys_path([
        "../",
        r"c:\test",
    ])
    assert parser.lines[18].strip() == "import os"
    assert parser.lines[19].strip() == "import sys"
    assert parser.lines[21].strip() == "sys.path.insert(0, os.path.abspath('../'))"
    assert parser.lines[22].strip() == "sys.path.insert(0, os.path.abspath('c:\\\\test'))"


if __name__ == "__main__":
    import pytest

    pytest.main()
