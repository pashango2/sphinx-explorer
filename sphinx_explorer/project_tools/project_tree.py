#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


# noinspection PyArgumentList
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
        return self.folder_icon if file_info.isDir() else self.file_icon


class ProjectTreeModel(QFileSystemModel):
    FileIconProvider = CustomFileIconProvider()

    @staticmethod
    def set_file_icons(*args, **kwargs):
        ProjectTreeModel.FileIconProvider.set_icon(*args, **kwargs)

    def __init__(self, project_path, parent=None):
        super(ProjectTreeModel, self).__init__(parent)
        self.setRootPath(project_path)
        self.setIconProvider(ProjectTreeModel.FileIconProvider)
