#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from sphinx_explorer.util import python_venv


# def test_pyenv():
#     env = python_venv.Env()
#     assert str(env) == "Default System Python"
#     assert str(python_venv.Env.from_str(env.to_str())) == "Default System Python"
#
#     env = python_venv.Env("anaconda", "py34", "anaconda_path")
#     assert str(env) == "py34(anaconda_path)"
#     assert str(python_venv.Env.from_str(env.to_str())) == "py34(anaconda_path)"
#
#     env = python_venv.Env("venv", "py34", "./py34")
#     assert str(env) == "py34(./py34)"
#     assert str(python_venv.Env.from_str(env.to_str())) == "py34(./py34)"


def test_search_anconda():
    v = python_venv.search_anaconda()
    print("anaconda:", v)
    env = python_venv.PythonVEnv(v)

    print(env.default_env())

    env.check_version()


def test_python_version():
    v = "Python 3.6.0 :: Continuum Analytics, Inc."
    r = python_venv.parse_python_version(v)
    assert r == "3.6.0"


def test_sys_env():
    env = python_venv.PythonVEnv()

    env_list = env.env_list()
    print(env_list)
