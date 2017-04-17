#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
from PySide.QtCore import *
import ast
import codecs
import os

from six import string_types

from sphinx_explorer.plugin import extension
from sphinx_explorer.plugin.extension import Extension


class CustomFileIconProvider(QFileIconProvider):
    def __init__(self, parent=None):
        super(CustomFileIconProvider, self).__init__(parent)
        self.folder_icon = None
        self.file_icon = None

    def set_icon(self, folder_icon, file_icon):
        self.folder_icon = folder_icon
        self.file_icon = file_icon

    def icon(self, file_info):
        # type: (QFileInfo) -> QIcon
        if file_info.isDir():
            return self.folder_icon
        else:
            return self.file_icon

        # return super(CustomFileIconProvider, self).icon(file_info)


class ProjectTreeModel(QFileSystemModel):
    FileIconProvider = CustomFileIconProvider()

    @staticmethod
    def set_file_icons(*args, **kwargs):
        ProjectTreeModel.FileIconProvider.set_icon(*args, **kwargs)

    def __init__(self, project_path, parent=None):
        super(ProjectTreeModel, self).__init__(parent)
        self.setRootPath(project_path)
        self.setIconProvider(ProjectTreeModel.FileIconProvider)