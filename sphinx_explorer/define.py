#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os

__version__ = "0.99"

message = """
Version: {}

https://github.com/pashango2/sphinx-explorer
""".format(__version__).strip()

SysPath = "."


def set_sys_path(sys_path):
    global SysPath
    SysPath = os.path.join(sys_path, "settings")


def get_sys_path():
    return SysPath
