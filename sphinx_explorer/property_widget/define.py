#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1

ADD_ICON = QIcon()


def set_icon(add_icon):
    global ADD_ICON
    ADD_ICON = add_icon
