#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import sys
import os
import fnmatch

Extensions = {}


def init(plugin_dir):
    global Extensions

    sys.path.insert(0, plugin_dir)

    Extensions = {}
    for root, dirs, files in os.walk(plugin_dir):
        for file_name in fnmatch.filter(files, "ext-*.py"):
            ext_name = file_name[:-len(".py")]
            # Extensions[ext_name] = toml.load(os.path.join(root, file_name))
            Extensions[ext_name] = __import__(ext_name)


def get(ext_name):
    return Extensions.get(ext_name)


def list_iter():
    for ext_name, ext in Extensions.items():
        yield ext_name, ext
