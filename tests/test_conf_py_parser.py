#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from sphinx_explorer.util import conf_py_parser

here = os.path.dirname(__file__)
conf_py_path = os.path.join("conf", "conf.py")


def test_parser():
    parser = conf_py_parser.Parser(conf_py_path)

    replace_dict = {
        "html_theme": str("sphinx_rtd_theme"),
    }
    lines = parser.replace(replace_dict)

    assert lines[84].strip() == "html_theme = 'sphinx_rtd_theme'"


if __name__ == "__main__":
    import pytest

    pytest.main()
