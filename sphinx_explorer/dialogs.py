#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
# noinspection PyPackageRequirements
import yaml
# from qtpy.QtCore import *
# from qtpy.QtGui import *
# from qtpy.QtWidgets import *
# from six import string_types
from .property_widget.frames import TreeDialog
from .project_list_model import ProjectItem


ProjectDialogSettings = """
- "#*Python Interpreter"
-
    - python:
        value_type: TypePython
        label: Python Interpreter,
        is_project: true
- "#* apidoc":
    label: Apidoc
-
    - "#autodoc_default_flags"
    -
        - members:
            value_type: TypeCheck
            default: yes
        - undoc-members:
            value_type: TypeCheck
            default: yes
        - private-members:
            value_type: TypeCheck
            default: no
        - special-members:
            value_type: TypeCheck
            default: no
        - inherited-members:
            value_type: TypeCheck
            default: no
        - show-inheritance:
            value_type: TypeCheck
            default: yes
- "#* Epub Settings"
-
    - epub_basename
    - epub_cover_image:
        value_type: TypeStaticImage
        title: "Open Cover Image"
        
    - epub_writing_mode
"""


# noinspection PyArgumentList
class ProjectSettingDialog(TreeDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, params_dict, project_item, parent=None):
        # type: (dict, ProjectItem, QWidget) -> None
        super(ProjectSettingDialog, self).__init__(parent)
        self.project_item = project_item

        settings = yaml.load(ProjectDialogSettings)
        self.property_model.load_settings(settings, params_dict)

        static_dir = os.path.join(project_item.source_dir_path(), "_static")
        item = self.property_model.get("Epub Settings").epub_cover_image
        item.params["path"] = project_item.source_dir_path()
        item.params["cwd"] = static_dir

        self.property_model.set_values(self.project_item.settings.settings)

        # epub_cover = self.property_model.get("Epub Settings").get("epub_cover_image")

    def accept(self):
        self.property_widget.teardown()
        dump = self.property_model.dump()
        self.project_item.settings.update(dump)
        self.project_item.settings.store()
        super(ProjectSettingDialog, self).accept()
