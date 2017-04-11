#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
from PySide.QtGui import *
from PySide.QtCore import *
from .sphinx_analyzer import SphinxInfo, QSphinxAnalyzer
from . import icon
from .util.exec_sphinx import quote
from six import string_types


class TemplateModel(QStandardItemModel):
    sphinxInfoLoaded = Signal(QModelIndex)
    autoBuildRequested = Signal(str, QStandardItem)

    def __init__(self, parent=None):
        super(TemplateModel, self).__init__(parent)

    def load_plugin(self, toml_path):
        # type: (string_types) -> None
        pass


class TemplateItem(QStandardItem):
    def __init__(self, name):
        super(TemplateItem, self).__init__(name)
        self.info = None    # type: SphinxInfo

    def path(self):
        # type: () -> string_types
        return self.text()

    def html_path(self):
        # type: () -> string_types
        if self.info.build_dir:
            return os.path.join(
                self.info.build_dir,
                "html", "index.html"
            )
        return None

    def has_html(self):
        # type: () -> bool
        return bool(self.html_path() and os.path.isfile(self.html_path()))

    def auto_build_command(self, target="html"):
        model = self.model()
        if model:
            cmd = "sphinx-autobuild -p 0 --open-browser {} {}".format(
                quote(self.info.source_dir),
                quote(os.path.join(self.info.build_dir, target)),
            )
            return cmd
        return None

    def auto_build(self, target="html"):
        cmd = self.auto_build_command(target)
        model = self.model()
        if model and cmd:
            model.autoBuildRequested.emit(cmd, self)

    def setInfo(self, info):
        # type: (SphinxInfo) -> None
        self.info = info

    def can_make(self):
        # type: () -> bool
        return bool(self.info and self.info.is_valid())

    def can_apidoc(self):
        # type: () -> bool
        return self.info.can_apidoc()
