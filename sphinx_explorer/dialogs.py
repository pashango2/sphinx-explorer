#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
# noinspection PyPackageRequirements
import yaml
# from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
# from six import string_types
from .property_widget.frames import TreeDialog


ProjectDialogSettings = """
- "#*Python Interpreter"
-
    - python:
        - value_type: TypePython
          label: Python Interpreter,
          is_project: true
- "#* Epub Settings"
-
    - epub_cover
    - epub_writing_mode
"""


# noinspection PyArgumentList
class ProjectSettingDialog(TreeDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, params_dict, project_item, parent=None):
        super(ProjectSettingDialog, self).__init__(parent)
        self.project_item = project_item

        settings = yaml.load(ProjectDialogSettings)
        self.property_model.load_settings(settings)

    def accept(self):
        self.property_widget.teardown()
        dump = self.property_model.dump(flat=True)
        print(dump)
        self.project_item.settings.set_venv_setting(dump.get("python"))
        self.project_item.settings.store()
        super(ProjectSettingDialog, self).accept()
