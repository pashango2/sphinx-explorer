#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

"""
This module manages Python's Virtual Environment.

* check python version
* search venv
"""
import os
import json
import fnmatch
import platform
import subprocess
import glob
from collections import OrderedDict
from six import string_types
from sphinx_explorer.util.commander import commander
from .tasks import *
from .package_model import *

if platform.system() == "Windows":
    import winreg

ICON_DICT = {
    "sys": None,
    "anaconda": None,
    "venv": None,
}

LINUX_CONDA_SEARCH_PATH = [
    (os.path.expanduser('~'), "anaconda*"),
    (os.path.expanduser('~'), "miniconda*"),
]

PYTHON_VERSION_RE = re.compile(r"Python ([^\s]*).*?")


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

    def python_path(self):
        e = Env.from_key(self.env)
        return e.python_path()

    def python_env(self):
        return Env.from_key(self.env)


class PythonVEnv(object):
    @staticmethod
    def create_system_python_env(venv_setting=None):
        # type: (VenvSetting) -> PythonVEnv
        """
        create system python envs.
        """
        system_env = search_system_python()
        conda_env = search_anaconda()

        venv_setting = venv_setting or VenvSetting()
        venv_list = []
        for path in venv_setting.search_venv_path:
            venv_list.extend(search_venv(path))

        env = PythonVEnv(system_env, conda_env, venv_list)
        env.check_version()

        return env

    def __init__(self, system_env=None, conda_env=None, venv_list=None):
        self._envs = OrderedDict()
        self._loading = False
        self.default_key = None

        if system_env:
            for env in system_env:
                key = env.key()
                self._envs[key] = env

        if conda_env:
            for env in conda_env:
                key = env.key()
                self._envs[key] = env

        if venv_list:
            for env in venv_list:
                key = env.key()
                self._envs[key] = env

        if not self._envs:
            env = Env()
            self._envs[env.key()] = env
            self.default_key = env.key()
        else:
            if self.default_key is None:
                for key in self._envs.keys():
                    self.default_key = key
                    break

    def get(self, key):
        # type: (str) -> Env
        return self._envs.get(key, self._envs[self.default_key])

    def default_env(self):
        return self._envs[self.default_key]

    def command(self, env=None):
        env = env or self.default_env()
        if env is None or env.path is None:
            return []

    def env_list(self, venv_list=None):
        result = []

        if venv_list:
            for env in venv_list:
                result.append((env.key(), env))

        for key, env in self._envs.items():
            result.append((key, env))

        return result

    def check_version(self):
        env_list = self.env_list()
        for key, env in env_list:
            python_path = env.python_path()
            if python_path:
                env.version = check_python_version(python_path)


class Env(object):
    @staticmethod
    def from_key(key):
        if key is None:
            return Env()
        keys = key.split(",")
        return Env(*keys)

    def __init__(self, env_type=None, name=None, path=None, version=None):
        self._type = env_type
        self.name = name
        self.path = path
        self.version = version

    def key(self):
        if self._type is None:
            return ""

        v = [(x or "") for x in [self._type, self.name, self.path, self.version]]
        return ",".join(v)

    def icon(self):
        return ICON_DICT.get(self._type or "sys")

    def type(self):
        return self._type or "sys"

    def __str__(self):
        # type: () -> string_types
        if self._type is None:
            return "System Python"

        if self.version:
            return "{} ({})".format(self.version, self.path)
        else:
            return "{} ({})".format(self.name, self.path)

    def python_path(self):
        if self.path is None:
            return "python"
        else:
            bin_path = "bin" if platform.system() != "Windows" else "Scripts"
            if self._type == "anaconda":
                return os.path.join(self.path, bin_path, "python")
            elif self._type == "venv":
                return os.path.join(self.path, bin_path, "python")
            elif self._type == "sys":
                return self.path

        return None

    def activate_command(self, cwd=None):
        if self.type() == "sys":
            return []

        if self.type() == "anaconda":
            if platform.system() == "Linux":
                # activate = os.path.join(self.path, "bin", "activate")
                return " ".join(["source activate " + self.name])
            else:
                return "activate " + self.name
        elif self.type() == "venv":
            if os.path.isabs(self.path):
                path = self.path
            else:
                path = os.path.join(cwd or "", self.path)

            path, _ = os.path.split(path)
            return os.path.join(path, _activate_cmd())

        raise ValueError(self.type())

    def to_str(self):
        return json.dumps([self._type, self.name, self.path])

    @staticmethod
    def from_str(s):
        if s == "System":
            return Env()

        try:
            return Env(*json.loads(s))
        except ValueError:
            return None


sys_env = PythonVEnv()


def setup(env):
    global sys_env
    sys_env = env


def search_anaconda():
    conda_path = "conda"

    if platform.system() == "Linux":
        break_flag = False
        for search_path, pattern in LINUX_CONDA_SEARCH_PATH:
            for path in fnmatch.filter(list(os.listdir(search_path)), pattern):
                conda_path = os.path.join(search_path, path, "bin", "conda")
                break_flag = True
                break
            if break_flag:
                break
        else:
            return []

    result = []
    if commander.check_exist([conda_path]):
        cmd = [
            conda_path, "info", "-e"
        ]

        val = commander.check_output(cmd, shell=True)
        if val:
            for line in val.splitlines():
                if line and line[0] == "#":
                    continue

                g = re.match(r"([^\s]*)([\s*]*)(.*?)$", line)
                if g:
                    name, default, path = g.groups()
                    if name:
                        result.append(Env("anaconda", name, path))

    return result


def _activate_path():
    if platform.system() == "Windows":
        return os.path.join("Scripts", "activate.bat")
    else:
        return os.path.join("bin", "activate")


def _activate_cmd():
    if platform.system() == "Windows":
        return "activate.bat"
    else:
        return "activate"


def _exe_path():
    if platform.system() == "Windows":
        return os.path.join("Scripts", "python.exe")
    else:
        return os.path.join("bin", "python")


def get_system_default_python():
    return commander.which("python")


def search_system_python():
    if platform.system() == "Windows":
        search_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Python\PythonCore"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Python\PythonCore"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Python\PythonCore"),
        ]

        path_list = set()
        for key, sub_key in search_keys:
            i = 0
            try:
                _key = winreg.OpenKey(key, sub_key)
            except OSError:
                continue

            # get version
            while True:
                try:
                    version = winreg.EnumKey(_key, i)
                except OSError:
                    break
                i += 1

                try:
                    path_key = winreg.OpenKey(
                        key,
                        sub_key + "\\" + version + "\\InstallPath"
                    )
                except OSError:
                    continue

                try:
                    _, value, value_type = winreg.EnumValue(path_key, 0)
                except OSError:
                    continue

                if value_type == winreg.REG_SZ:
                    path_list.add(os.path.join(value, "python.exe"))
    else:
        path_list = set()
        for python_path in glob.glob("/usr/bin/python*"):
            if os.path.islink(python_path):
                continue
            path_list.add(python_path)

    env_list = []
    for python_path in path_list:
        # for pythonX.Xm
        if python_path[-1] == "m":
            continue

        version = check_python_version(python_path)
        if version:
            env = Env("sys", path=python_path, version=version)
            env_list.append(env)

    return env_list


def search_venv(path, cwd=None):
    # find virtual env
    result = []

    if os.path.isdir(path):
        for x in os.listdir(path):
            if os.path.isdir(os.path.join(path, x)):
                activate_path = os.path.join(path, x, _activate_path())
                exe_path = os.path.join(path, x, _exe_path())
                if os.path.isfile(activate_path) and os.path.isfile(exe_path):
                    version = check_python_version(exe_path)
                    if cwd:
                        exe_path = os.path.relpath(exe_path, cwd)
                    result.append(Env("venv", x, exe_path, version))
    elif os.path.isfile(path):
        version = check_python_version(path)
        if cwd:
            path = os.path.relpath(path, cwd)
        result.append(Env("venv", path, path, version))

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


def activate_command(venv_setting, cwd=None):
    # type: (VenvSetting, str) -> str
    if venv_setting is None:
        return ""

    env = Env.from_key(venv_setting.env)
    return env.activate_command(cwd)
