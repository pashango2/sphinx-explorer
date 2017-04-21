#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import re
import json
import platform
from collections import OrderedDict
from six import string_types
from . import exec_sphinx

ICON_DICT = {
    "sys": None,
    "anaconda": None,
    "venv": None,
}


class Env(object):
    def __init__(self, env_type=None, name=None, path=None):
        self.type = env_type
        self.name = name
        self.path = path

    def __str__(self):
        # type: () -> string_types
        if self.type is None or self.name is None or self.path is None:
            return "Default System Python"
        return "{}({})".format(self.name, self.path)

    def command(self, cwd=None):
        if self.type is None or self.type == "sys":
            return []

        if self.type == "anaconda":
            if platform.system() == "Linux":
                return ["source activate " + self.name]
            else:
                return ["activate " + self.name]
        elif self.type == "venv":
            if os.path.isabs(self.path):
                path = self.path
            else:
                path = os.path.join(cwd or "", self.path)

            return [os.path.join(path, _env_path())]

        raise ValueError(self.type)

    def to_str(self):
        return json.dumps([self.type, self.name, self.path])

    @staticmethod
    def from_str(s):
        if s == "System":
            return Env()

        try:
            return Env(*json.loads(s))
        except ValueError:
            return None


class PythonVEnv(object):
    def __init__(self, conda_env=None, venv_list=None):
        self._envs = OrderedDict()
        env = Env("sys", "System Default", None)
        self._envs[env.to_str()] = env
        self._default_env = env.to_str()

        if conda_env:
            for name, default, path in conda_env:
                env = Env("anaconda", name, path)
                key = env.to_str()
                self._envs[key] = env

                if default:
                    self._default_env = key

        if venv_list:
            for env in venv_list:
                key = env.to_str()
                self._envs[key] = env

    def default_env(self):
        return self._envs[self._default_env]

    def command(self, env=None):
        env = env or self.default_env()
        if env is None or env.path is None:
            return []

    def env_list(self, venv_list=None):
        result = []

        if venv_list:
            for env in venv_list:
                result.append((env.to_str(), env))

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


def python_venv(cwd, fullpath=False):
    # find venv
    result = []

    env = _env_path()
    for x in os.listdir(cwd):
        if os.path.isdir(os.path.join(cwd, x)):
            activate_path = os.path.join(cwd, x, env)
            if os.path.exists(activate_path):
                path = os.path.join(cwd, x) if fullpath else x
                result.append(Env("venv", x, path))

    return result


def get_path(venv_info, cwd=None):
    if venv_info is None:
        return []

    return venv_info.command(cwd)

