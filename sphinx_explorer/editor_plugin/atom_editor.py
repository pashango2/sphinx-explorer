#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

ATOM_PATH = "atom"


def open(path):
    # print(" ".join([ATOM_PATH, path]))
    subprocess.Popen([ATOM_PATH, path], shell=True)
