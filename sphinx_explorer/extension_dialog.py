#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
# from PySide.QtCore import *
from .plugin_dialog import PluginDialog


ExtensionPluginDir = "extension"


class ExtensionDialog(PluginDialog):
    def __init__(self, parent=None):
        # type: (QWidget) -> None
        super(ExtensionDialog, self).__init__(ExtensionPluginDir, parent)
