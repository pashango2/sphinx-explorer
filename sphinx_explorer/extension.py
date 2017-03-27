#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import fnmatch
import toml

Extensions = {}


def init(plugin_dir):
    global Extensions

    Extensions = {}
    for root, dirs, files in os.walk(plugin_dir):
        for file_name in fnmatch.filter(files, "*.toml"):
            ext_name = file_name[:-len(".toml")]
            Extensions[ext_name] = toml.load(os.path.join(root, file_name))


def get(ext_name):
    return Extensions.get(ext_name)
