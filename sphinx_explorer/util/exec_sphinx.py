#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import subprocess
import platform


TERM_ENCODING = getattr(sys.stdin, 'encoding', None)


def _cmd(cmd):
    # type: (str) -> str
    if platform.system() in ("Windows", "Darwin"):
        return cmd
    else:
        return " ".join(['/bin/bash', '-i', '-c', cmd])


def check_output(cmd):
    # type: (str) -> str
    return subprocess.check_output(_cmd(cmd), shell=True).decode(TERM_ENCODING)


def exec_(cmd):
    # type: (str) -> bool
    p = subprocess.Popen(_cmd(cmd), shell=True)
    p.wait()

    return p.returncode == 0

