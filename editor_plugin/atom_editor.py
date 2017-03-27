#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

ATOM_PATH = "atom"


def open_dir(path):
    assert path
    subprocess.Popen([ATOM_PATH, "."], cwd=path, shell=True)
