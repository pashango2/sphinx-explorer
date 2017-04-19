#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1

ADD_ICON = QIcon()
UP_ICON = QIcon()
DOWN_ICON = QIcon()
DELETE_ICON = QIcon()


def set_icon(**params):
    global ADD_ICON, UP_ICON, DOWN_ICON, DELETE_ICON

    ADD_ICON = params.get("add_icon")
    UP_ICON = params.get("up_icon")
    DOWN_ICON = params.get("down_icon")
    DELETE_ICON = params.get("delete_icon")
