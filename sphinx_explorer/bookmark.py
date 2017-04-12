#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *


class Bookmark(QObject):
    def __init__(self, parent=None):
        super(Bookmark, self).__init__(parent)
        self.parent = None
        # self.add_action = QAction("Add Bookmark")
        self.select_action = QAction("Select Bookmark")

    def set_parent(self, parent):
        self.parent = parent
