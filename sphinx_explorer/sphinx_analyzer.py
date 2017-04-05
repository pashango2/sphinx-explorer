#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import toml
from six import string_types
from PySide.QtCore import *
from PySide.QtGui import *


class SphinxInfo(object):
    SETTING_NAME = "setting.toml"

    def __init__(self, path):
        self.path = path
        self.conf_py_path = None
        self.source_dir = None
        # self.conf = {}
        self.settings = {}

        self._analyze()

    def _analyze(self):
        # search conf.py
        self.conf_py_path = self._find_conf_py(self.path)
        self.source_dir = os.path.dirname(self.conf_py_path) if self.conf_py_path else None
        self.settings = {}

        path = os.path.join(self.path, self.SETTING_NAME)
        if os.path.isfile(path):
            self.settings = toml.load(path)

    # def read_conf(self):
    #     if self.conf_py_path:
    #         self.conf = config(self.conf_py_path)

    def is_valid(self):
        # type: () -> bool
        return bool(self.conf_py_path)

    @staticmethod
    def _find_conf_py(path):
        # type: (str) -> str or None
        assert path

        _path = os.path.join(path, "conf.py")
        if os.path.isfile(_path):
            return _path

        _path = os.path.join(path, "source", "conf.py")
        if os.path.isfile(_path):
            return _path

        return None

    @property
    def auto_build_setting(self):
        return self.settings.get("autobuild", {})

    @property
    def build_dir(self):
        # type: () -> string_types
        return os.path.join(self.path, self.settings.get("build_dir"))

    def can_apidoc(self):
        # type: () -> bool
        return bool("apidoc" in self.settings and self.settings["apidoc"].get("module_dir"))


class QSphinxAnalyzer(QObject, QRunnable):
    finished = Signal(SphinxInfo, QStandardItem)

    def __init__(self, doc_path, item):
        # type: (str, QStandardItem) -> None
        QObject.__init__(self)
        QRunnable.__init__(self)

        self.doc_path = doc_path
        self.item = item

    def run(self):
        info = SphinxInfo(self.doc_path)
        # if info.conf_py_path:
        #     info.read_conf()
        self.finished.emit(info, self.item)
