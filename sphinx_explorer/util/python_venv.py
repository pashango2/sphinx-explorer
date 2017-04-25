#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import re
import json
import fnmatch
import platform
import subprocess
from collections import OrderedDict
from six import string_types
from .commander import commander, quote

ICON_DICT = {
    "sys": None,
    "anaconda": None,
    "venv": None,
}

CONDA_LINUX_SEARCH_PATH = {
    (os.path.expanduser('~'), "anaconda*"),
    (os.path.expanduser('~'), "miniconda*"),
}

PYTHON_VERSION_RE = re.compile(r"Python ([^\s]*).*?")


class Env(object):
    def __init__(self, env_type=None, name=None, path=None, version=None):
        self.type = env_type
        self.name = name
        self.path = path
        self.version = version

    def __str__(self):
        # type: () -> string_types
        if self.path is None:
            if self.version:
                return "{} ({})".format(self.version, self.name)
            else:
                return self.name

        if self.version:
            return "{} ({})".format(self.version, self.path)
        else:
            return "{} ({})".format(self.name, self.path)

    def python_path(self):
        if self.path is None:
            return "python"
        else:
            bin_path = "bin" if platform.system() != "Windows" else "Scripts"
            if self.type == "anaconda":
                return os.path.join(self.path, bin_path, "python")
            elif self.type == "venv":
                return os.path.join(self.path, bin_path, "python")

        return None

    def command(self, cwd=None):
        if self.type is None or self.type == "sys":
            return []

        if self.type == "anaconda":
            if platform.system() == "Linux":
                activate = os.path.join(self.path, "bin", "activate")
                return " ".join(["source " + activate + " " + self.name])
            else:
                return "activate " + self.name
        elif self.type == "venv":
            if os.path.isabs(self.path):
                path = self.path
            else:
                path = os.path.join(cwd or "", self.path)

            return os.path.join(path, _env_path())

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


class VenvSetting(dict):
    def __init__(self, value=None):
        super(VenvSetting, self).__init__()
        value = value or {}
        self["env"] = value.get("env")
        self["search_venv_path"] = value.get("search_venv_path", [])

    @property
    def search_venv_path(self):
        return self["search_venv_path"]

    def set_search_venv_path(self, path):
        self["search_venv_path"] = path

    @property
    def env(self):
        return self["env"]

    def set_env(self, env):
        self["env"] = env


class PythonVEnv(object):
    def __init__(self, conda_env=None, venv_list=None):
        self._envs = OrderedDict()
        env = Env("sys", "System Default", None)
        self._envs[env.to_str()] = env
        self._default_env = env.to_str()
        self._loading = False

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

    def default_env_key(self):
        return self._default_env

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

    def check_version(self):
        env_list, _ = self.env_list()
        for key, env in env_list:
            python_path = env.python_path()
            if python_path:
                env.version = check_python_version(python_path)

    def set_anaconda_env(self, env):
        pass


sys_env = PythonVEnv()


def setup(env):
    global sys_env
    sys_env = env


def search_anaconda():
    conda_path = "conda"

    if platform.system() == "Linux":
        break_flag = False
        for search_path, pattern in CONDA_LINUX_SEARCH_PATH:
            for path in fnmatch.filter(list(os.listdir(search_path)), pattern):
                conda_path = os.path.join(search_path, path, "bin", "conda")
                break_flag = True
                break
            if break_flag:
                break
        else:
            return []

    cmd = [
        conda_path, "info", "-e"
    ]

    val = commander.check_output(cmd, shell=True)
    if val:
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


def search_venv(cwd, fullpath=False):
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


def check_python_version(path):
    ret = commander.check_output([path, "--version"], stderr=subprocess.STDOUT, shell=True)

    if ret:
        return parse_python_version(ret)

    return None


def parse_python_version(text):
    g = PYTHON_VERSION_RE.match(text)
    if g:
        return g.group(1)
    return None


def get_path(venv_info, cwd=None):
    if venv_info is None:
        return []

    return venv_info.command(cwd)

