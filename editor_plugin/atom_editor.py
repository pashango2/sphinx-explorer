#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

ATOM_PATH = "atom"


# noinspection PyShadowingBuiltins
def open(path):
    assert path
    print(path)
    subprocess.Popen([ATOM_PATH, path], shell=True)
