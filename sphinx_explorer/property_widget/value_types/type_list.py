#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .type_base import TypeBase
from ..widgets import *


class BaseTypeList(TypeBase):
    WidgetClass = MovableListWidget

    @classmethod
    def control(cls, _, parent):
        return cls.WidgetClass(parent)

    @classmethod
    def value(cls, control):
        return control.to_list()

    @staticmethod
    def data(data):
        if isinstance(data, (list, tuple)):
            return "\n".join(data)
        return data

    @classmethod
    def set_value(cls, control, value):
        # type: (FontListWidget, list) -> None
        if value:
            control.addItems(value)
            for row in range(control.count()):
                item = control.item(row)
                item.setFlags(item.flags() | Qt.ItemIsEditable)

    @classmethod
    def sizeHint(cls):
        return QSize(-1, 180)

    @classmethod
    def setup(cls, item):
        item.setData(Qt.AlignTop | Qt.AlignLeft, Qt.TextAlignmentRole)


class TypeFontList(BaseTypeList):
    WidgetClass = FontListWidget


class TypeDirList(BaseTypeList):
    WidgetClass = DirListWidget
