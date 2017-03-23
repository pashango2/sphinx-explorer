#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
from PySide.QtCore import *
import os
from .util import sphinx_config


class SphinxInfo(object):
    def __init__(self, path):
        self.path = path
        self.conf_py_path = None
        self.conf = {}

        self._analyze()

    def _analyze(self):
        self.conf_py_path = self._find_conf_py(self.path)

    def read_conf(self):
        self.conf = sphinx_config.get(self.conf_py_path)

    @staticmethod
    def _find_conf_py(path):
        # type: (str) -> str or None
        assert path
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if file_name == "conf.py":
                    return os.path.join(root, file_name)
        return None


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
        info.read_conf()
        self.finished.emit(info, self.item)
