#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals


class DefaultValues(object):
    def __init__(self, values_dict=None):
        self._dicts = [values_dict or {}]

    def __getitem__(self, key):
        for d in self._dicts:
            if key in d:
                return d[key]
        raise KeyError(key)

    def __contains__(self, key):
        for d in self._dicts:
            if key in d:
                return True
        return False

    def set_default_value(self, key, value):
        d = {key: value}
        self._dicts.insert(0, d)

    def items(self):
        for key in self.keys():
            yield key, self[key]

    def get(self, key, default=None, parent=None):
        for d in self._dicts:
            if parent:
                break_flag = False
                for pkey in parent:
                    if pkey in d:
                        d = d[pkey]
                    else:
                        break_flag = True
                        break
                if break_flag:
                    continue

            if key in d:
                return d[key]
        return default

    def push(self, d):
        self._dicts.insert(0, d or {})

    def pop(self, index=0):
        index = len(self._dicts) - 1 - index
        if index < 0:
            return
        try:
            self._dicts.pop(index)
        except IndexError:
            pass

    def keys(self):
        keys = set()
        for d in self._dicts:
            keys |= set(d.keys())
        return keys

    def copy(self):
        d = {}
        for key, value in self.items():
            d[key] = value
        return d
