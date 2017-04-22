#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *


class Bookmark(QObject):
    def __init__(self, parent=None):
        super(Bookmark, self).__init__(parent)
        self.parent = None
        # self.add_action = QAction("Add Bookmark")
        self.select_action = QAction("Select Bookmark", self)

    def set_parent(self, parent):
        self.parent = parent
