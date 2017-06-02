#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from qtpy.QtCore import *


class Page(QObject):
    pass


from .wizard_pages import *
from .form_layout import *