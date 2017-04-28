#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .package_model import PackageModel, PackageItem
from .tasks import *

package_dict = {}
g_parent = None


def init(parent):
    global g_parent
    g_parent = parent


def get_model(python_path):
    global package_dict, g_parent

    if python_path not in package_dict:
        model = PackageModel(g_parent)
        package_dict[python_path] = model
    else:
        model = package_dict[python_path]

    return model
