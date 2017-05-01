#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json

# noinspection PyUnresolvedReferences
from qtpy.QtCore import *
# noinspection PyUnresolvedReferences
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from .property_model import PropertyItem, CategoryItem, PropertyModel
from .property_model import PropertyItemType
from .description_widget import DescriptionWidget
from .default_value_dict import DefaultValues
from .define import set_icon, cog_icon
from .property_widget import PropertyWidget

from .value_types import *  # NOQA


if False:
    from typing import Dict, Iterator
    from six import string_types

__all__ = [
    "PropertyWidget",
    "PropertyModel",
    "TypeBase",
    "TypeBool",
    "TypeDirPath",
    "TypeChoice",
    "TypeFontList"
    "register_value_type",
    "find_value_type",
    "DescriptionWidget",
    "DefaultValues",
    "set_icon"
]

__version__ = "1.0"
__release__ = __version__ + "b"


