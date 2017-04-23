#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.util import python_venv


def test_pyenv():
    env = python_venv.Env()
    assert str(env) == "Default System Python"
    assert str(python_venv.Env.from_str(env.to_str())) == "Default System Python"

    env = python_venv.Env("anaconda", "py34", "anaconda_path")
    assert str(env) == "py34(anaconda_path)"
    assert str(python_venv.Env.from_str(env.to_str())) == "py34(anaconda_path)"

    env = python_venv.Env("venv", "py34", "./py34")
    assert str(env) == "py34(./py34)"
    assert str(python_venv.Env.from_str(env.to_str())) == "py34(./py34)"



