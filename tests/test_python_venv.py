#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from sphinx_explorer import python_venv


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
    env.check_version()

    for key, env in env.env_list():
        print(key, env)


def test_python_version():
    v = "Python 3.6.0 :: Continuum Analytics, Inc."
    r = python_venv.parse_python_version(v)
    assert r == "3.6.0"


def test_sys_env():
    env = python_venv.PythonVEnv()
    env_list = env.env_list()

    assert str(env.get(env.default_key)) == "System Python"
    assert str(env.default_env()) == "System Python"

    for key, env in env_list:
        print(key, env)


def test_venv():
    py34 = python_venv.Env("venv", "py34", "py34_path", "3.4")
    py35 = python_venv.Env("venv", "py35", "py35_path", "3.5")

    env = python_venv.PythonVEnv(venv_list=[py34, py35])
    env_list = env.env_list()

    assert env_list[0][0] == ""
    assert str(env_list[0][1]) == "System Python"
    assert env_list[1][0] == "venv,py34,py34_path,3.4"
    assert str(env_list[1][1]) == "3.4 (py34_path)"
    assert env_list[2][0] == "venv,py35,py35_path,3.5"
    assert str(env_list[2][1]) == "3.5 (py35_path)"


