#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import re
import platform
from collections import namedtuple
from . import exec_sphinx

Env = namedtuple("Env", "type name path")

ICON_DICT = {
    "sys": None,
    "anaconda": None,
    "venv": None,
}


class PythonVEnv(object):
    def __init__(self, conda_env=None):
        self._envs = {
            "System": Env("sys", "System Default", None)
        }
        self._default_env = "System"

        if conda_env:
            for name, default, path in conda_env:
                key = "anaconda.name"
                self._envs[key] = Env(
                    "anaconda",
                    name,
                    path
                )

                if default:
                    self._default_env = key

    def default_env(self):
        return self._envs[self._default_env]

    def command(self, env=None):
        env = env or self.default_env()
        if env is None or env.path is None:
            return []

    def env_list(self, venv_list=None):
        result = []

        if venv_list:
            for name, path in venv_list:
                key = "{}.{}".format("venv", path)
                env = Env("venv", name, path)
                result.append((key, env))

        for key, env in self._envs.items():
            result.append((key, env))
        return result, self._default_env

    def set_anaconda_env(self, env):
        pass


sys_env = PythonVEnv()


def setup(env):
    global sys_env
    sys_env = env


def anaconda_env():
    cmd = [
        "conda", "info", "-e"
    ]

    ret, val = exec_sphinx.check_output(" ".join(cmd), stderr=None)
    if ret == 0:
        result = []
        for line in val.splitlines():
            if line and line[0] == "#":
                continue

            g = re.match(r"([^\s]*)([\s*]*)(.*?)$", line)
            if g:
                name, default, path = g.groups()
                if name:
                    result.append((name, "*" in default, path))

        return result
    return []


def _env_path():
    if platform.system() == "Windows":
        return os.path.join("Scripts", "activate.bat")
    else:
        return os.path.join("bin", "activate")


def python_venvs(cwd):
    # find venv
    result = []

    env = _env_path()
    for x in os.listdir(cwd):
        if os.path.isdir(os.path.join(cwd, x)):
            activate_path = os.path.join(cwd, x, env)
            if os.path.exists(activate_path):
                result.append((x, os.path.join(cwd, x)))

    return result


def get_path(venv_info):
    if venv_info is None:
        return None

    env_type, path = venv_info.split(".")
    if env_type.strip() == "venv":
        return path.strip()

    return None