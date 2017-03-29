#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
import os
import platform
import subprocess
import sys

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)


def _cmd(cmd):
    # type: (str) -> str
    if platform.system() in ("Windows", "Darwin"):
        return cmd
    else:
        return " ".join(['/bin/bash', '-i', '-c', '"' + cmd + '"'])


def check_output(cmd):
    # type: (str) -> str
    cmd = _cmd(cmd)
    return subprocess.check_output(cmd, shell=True).decode(TERM_ENCODING)


def config(config_path):
    # type: (str) -> str or None
    result = check_output(
        " ".join([
            "python", os.path.join("script", "sphinx_config.py"), config_path
        ])
    )
    return json.loads(result) if result else None


def exec_(cmd, cwd=None):
    # type: (str, str) -> bool
    cmd = _cmd(cmd)
    return subprocess.call(cmd, cwd=cwd, shell=True) == 0


def launch(cmd, cwd=None):
    # type: (str, str) -> None
    cmd = _cmd(cmd)

    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(cmd, cwd=cwd, shell=True, startupinfo=startupinfo)
    else:
        subprocess.Popen(cmd, cwd=cwd, shell=True)
