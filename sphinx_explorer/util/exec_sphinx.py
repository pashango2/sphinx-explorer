#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
import os
import platform
import subprocess
import sys
from six import string_types

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


def _encoding():
    return TERM_ENCODING or sys.getfilesystemencoding()


def command(cmd):
    # type: (string_types) -> string_types
    if platform.system() in ("Windows", "Darwin"):
        return cmd
    else:
        return " ".join(['/bin/bash', '-i', '-c', '"' + cmd + '"'])


def create_cmd(cmds):
    # type: ([string_types]) -> string_types
    str_cmd = " ".join([
        quote(x)
        for x in cmds
        if x
    ])

    return command(str_cmd)


def check_output(cmd):
    # type: (string_types) -> (int, string_types)
    cmd = command(cmd)

    try:
        output = subprocess.check_output(
            cmd.encode(_encoding()),
            shell=True,
        )
    except subprocess.CalledProcessError as exc:
        return exc.returncode, exc.output

    return 0, output.decode(_encoding()) if output else None


def config(config_path):
    # type: (string_types) -> string_types or None
    _, result = check_output(
        " ".join([
            "python", os.path.join(os.path.dirname(sys.argv[0]), "script", "sphinx_config.py"), config_path
        ])
    )
    return json.loads(result) if result else None


def exec_(cmd, cwd=None):
    # type: (string_types, string_types) -> int
    shell = True

    if platform.system() == "Windows":
        cmd = command(('cmd.exe /C "' + cmd + '"')).encode(_encoding())
        shell = False

    p = subprocess.Popen(
        cmd,
        cwd=cwd.encode(_encoding()) if cwd else None,
        shell=shell,
    )
    p.wait()
    return p.returncode


def launch(cmd, cwd=None):
    # type: (string_types, string_types or None) -> None
    cmd = command(cmd)

    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(
            cmd.encode(_encoding()),
            cwd=cwd.encode(sys.getfilesystemencoding()),
            shell=True,
            startupinfo=startupinfo
        )
    else:
        subprocess.Popen(cmd, cwd=cwd, shell=True)


def console(cmd, cwd=None):
    # type: (string_types, string_types) -> None or subprocess.Popen
    if platform.system() == "Windows":
        cmd = command(cmd)
        return subprocess.Popen(
            cmd.encode(_encoding()),
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    elif platform.system() == "Linux":
        cmd = "gnome-terminal -e '/bin/bash -i -c \"{}\"'".format(cmd)
        return subprocess.Popen(cmd, cwd=cwd, shell=True)
    else:
        # cmd = command(cmd)
        # subprocess.Popen(cmd, cwd=cwd, shell=True)
        print(platform.system())
        return None


def show_directory(path):
    # type: (string_types) -> None
    path = os.path.normpath(path)
    if platform.system() == "Windows":
        cmd = ["explorer", path]
    elif platform.system() == "Darwin":
        cmd = ["open", path]
    else:
        cmd = ["xdg-open", path]

    launch(" ".join(cmd), path)


def open_terminal(path):
    # type: (string_types) -> None
    if platform.system() == "Windows":
        subprocess.Popen("cmd", cwd=os.path.normpath(path).encode(_encoding()))
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", os.path.normpath(path)])
    else:
        subprocess.Popen("gnome-terminal", cwd=os.path.normpath(path))
