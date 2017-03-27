#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import toml
from collections import OrderedDict


class Settings(OrderedDict):
    def __init__(self):
        super(Settings, self).__init__()

    @staticmethod
    def load(fd_toml):
        return toml.load(fd_toml, Settings)

    def dump(self):
        pass

