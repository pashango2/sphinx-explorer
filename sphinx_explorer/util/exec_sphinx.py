#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
import json
import subprocess
import platform


TERM_ENCODING = getattr(sys.stdin, 'encoding', None)


def _cmd(cmd):
    # type: (str) -> Tuple[str, bool]
    if platform.system() in ("Windows", "Darwin"):
        return cmd, True
    else:
        return " ".join(['/bin/bash', '-i', '-c', '"' + cmd + '"']), True


def check_output(cmd):
    # type: (str) -> str
    cmd, shell = _cmd(cmd)
    return subprocess.check_output(cmd, shell=shell)


def config(config_path):
    result = check_output(
        " ".join([
            "python", os.path.join("script", "sphinx_config.py"), config_path
        ])
    )
    return json.loads(result) if result else None


def exec_(cmd, cwd=None):
    # type: (str, str) -> bool
    cmd, shell = _cmd(cmd)
    return subprocess.call(cmd, cwd=cwd, shell=shell) == 0


def launch(cmd, cwd=None):
    # type: (str, str) -> None
    cmd, shell = _cmd(cmd)

    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.STARTF_USESHOWWINDOW
    else:
        startupinfo = subprocess.STARTUPINFO()

    subprocess.Popen(cmd, cwd=cwd, shell=shell, startupinfo=startupinfo)


