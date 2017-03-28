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
    print(cmd)
    return subprocess.check_output(cmd, shell=shell).decode(TERM_ENCODING)


def config(config_path):
    result = check_output(
        " ".join([
            "python", os.path.join("script", "sphinx_config.py"), config_path
        ])
    )
    return json.loads(result)


def exec_(cmd):
    # type: (str) -> bool
    cmd, shell = _cmd(cmd)
    print(cmd)
    p = subprocess.Popen(cmd, shell=shell)
    p.wait()

    return p.returncode == 0

