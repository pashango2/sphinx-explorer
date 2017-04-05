#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
import os
import platform
import subprocess
import sys

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)

if platform.system() == "Windows":
    def quote(s):
        if " " in s:
            return '"' + s + '"'
        return s
else:
    try:
        from shlex import quote
    except ImportError:
        from pipes import quote


def command(cmd):
    # type: (str) -> str
    if platform.system() in ("Windows", "Darwin"):
        return cmd
    else:
        return " ".join(['/bin/bash', '-i', '-c', '"' + cmd + '"'])


def check_output(cmd):
    # type: (str) -> str
    cmd = command(cmd)
    return subprocess.check_output(cmd, shell=True).decode(TERM_ENCODING)


def config(config_path):
    # type: (str) -> str or None
    result = check_output(
        " ".join([
            "python", os.path.join(os.path.dirname(sys.argv[0]), "script", "sphinx_config.py"), config_path
        ])
    )
    return json.loads(result) if result else None


def exec_(cmd, cwd=None):
    # type: (str, str) -> bool
    cmd = command(cmd)
    return subprocess.call(cmd, cwd=cwd, shell=True) == 0


def launch(cmd, cwd=None):
    # type: (str, str) -> None
    cmd = command(cmd)

    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(cmd, cwd=cwd, shell=True, startupinfo=startupinfo)
    else:
        subprocess.Popen(cmd, cwd=cwd, shell=True)


def console(cmd, cwd=None):
    # type: (str, str) -> None
    if platform.system() == "Windows":
        cmd = 'cmd.exe /K "{}"'.format(command(cmd))
        subprocess.Popen(cmd, cwd=cwd)
    elif platform.system() == "Linux":
        cmd = "gnome-terminal -e '/bin/bash -i -c \"{}\"'".format(cmd)
        subprocess.Popen(cmd, cwd=cwd, shell=True)
    else:
        # cmd = _cmd(cmd)
        # subprocess.Popen(cmd, cwd=cwd, shell=True)
        print(platform.system())


def show_directory(path):
    # type: (str) -> None
    path = os.path.normpath(path)
    if platform.system() == "Windows":
        cmd = ["explorer", path]
    elif platform.system() == "Darwin":
        cmd = ["open", path]
    else:
        cmd = ["xdg-open", path]

    launch(" ".join(cmd), path)


def open_terminal(path):
    # type: (str) -> None
    if platform.system() == "Windows":
        subprocess.Popen("cmd", cwd=os.path.normpath(path))
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", os.path.normpath(path)])
    else:
        subprocess.Popen("gnome-terminal", cwd=os.path.normpath(path))
