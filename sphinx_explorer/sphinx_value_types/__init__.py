#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from .sphinx_value_types import *
from sphinx_explorer.property_widget import register_value_type


# noinspection PyTypeChecker
def init():
    register_value_type(TypeLanguage)
    register_value_type(TypeHtmlTheme)
    register_value_type(TypePython)
    register_value_type(TypeStaticImage)
