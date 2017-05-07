#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .type_base import *
from .type_list import *


AllTypes = [
    TypeBool,
    TypeCheck,
    TypeDirPath,
    TypeRelDirPath,
    TypeChoice,
    TypeFontList,
    TypeDirList,
]


def register_value_type(value_type):
    # type: (TypeBase) -> None
    global AllTypes
    AllTypes.append(value_type)


def find_value_type(type_name, params=None):
    # type: (string_types, dict or None) -> TypeBase or None
    for value_type in AllTypes:
        if value_type.__name__ == type_name:
            return value_type.create(params)
    return None
