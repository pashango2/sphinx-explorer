#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

EXE_PATH = "code"


def open_dir(path):
    assert path
    subprocess.Popen([EXE_PATH, "."], cwd=path, shell=True)
