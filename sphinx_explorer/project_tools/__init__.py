#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# from PySide.QtGui import *
# from PySide.QtCore import *
from qtpy.QtCore import *
from .project_tree import ProjectTreeModel


class ProjectTools(QObject):
    def __init__(self, project_path, parent=None):
        super(ProjectTools, self).__init__(parent)
        self.project_path = project_path
        self.file_model = ProjectTreeModel(self.project_path, self)

    @staticmethod
    def set_file_icons(*args, **kwargs):
        ProjectTreeModel.set_file_icons(*args, **kwargs)
