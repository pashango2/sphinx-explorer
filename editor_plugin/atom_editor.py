#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import shlex

ATOM_PATH = "atom"


# noinspection PyShadowingBuiltins
def open(path):
    assert path
    subprocess.Popen([ATOM_PATH, '"' + shlex.quote(path) + '"'], shell=True)
