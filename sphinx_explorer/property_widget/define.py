#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from qtpy.QtCore import *
from qtpy.QtGui import *
# from qtpy.QtWidgets import *

CategoryItemType = QStandardItem.UserType + 1
PropertyItemType = CategoryItemType + 1

ADD_ICON = QIcon()
UP_ICON = QIcon()
DOWN_ICON = QIcon()
DELETE_ICON = QIcon()
COG_ICON = QIcon()


def set_icon(**params):
    global ADD_ICON, UP_ICON, DOWN_ICON, DELETE_ICON, COG_ICON

    ADD_ICON = params.get("add_icon", ADD_ICON)
    UP_ICON = params.get("up_icon", UP_ICON)
    DOWN_ICON = params.get("down_icon", DOWN_ICON)
    DELETE_ICON = params.get("delete_icon", DELETE_ICON)
    COG_ICON = params.get("cog_icon", COG_ICON)
