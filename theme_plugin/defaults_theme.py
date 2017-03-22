#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals


class ThemeBase(object):
    pass


class DefaultTheme(ThemeBase):
    Name = "default"
    ThemeName = "default"


class BasicTheme(ThemeBase):
    Name = "basic"
    ThemeName = "basic"


class SphinxDocTheme(ThemeBase):
    Name = "sphinxdoc"
    ThemeName = "sphinxdoc"


class AgogoTheme(ThemeBase):
    Name = "agogo"
    ThemeName = "agogo"


class NatureTheme(ThemeBase):
    Name = "nature"
    ThemeName = "nature"


class PyramidTheme(ThemeBase):
    Name = "pyramid"
    ThemeName = "pyramid"


class HaikuTheme(ThemeBase):
    Name = "haiku"
    ThemeName = "haiku"


class TraditionalTheme(ThemeBase):
    Name = "traditional"
    ThemeName = "traditional"


class EpubTheme(ThemeBase):
    Name = "epub"
    ThemeName = "epub"


class BizStyleTheme(ThemeBase):
    Name = "bizstyle"
    ThemeName = "bizstyle"
