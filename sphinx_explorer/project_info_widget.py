#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from qtpy.QtCore import *
# from qtpy.QtGui import *
from qtpy.QtWidgets import *
import yaml
# from .ui.main_window_ui import Ui_MainWindow
# from .sphinx_value_types.widgets import PythonComboButton
from .project_list_model import ProjectItem
from .property_widget import PropertyModel
from .python_venv import sys_env
from .ui.extension_widget_ui import Ui_Form


PROJECT_SETTINGS = """
- "#* Epub Settings"
-
    - epub_basename
    - epub_cover_image:
        value_type: TypeStaticImage
        title: "Open Cover Image"
        
    - epub_writing_mode
- "#* Auto Class"
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
"""


class ProjectInfoWidget(QObject):
    def __init__(self, ui, params_dict, parent):
        super(ProjectInfoWidget, self).__init__(parent)
        self._parent = parent
        self.ui = ui

        self.project_setting_model = PropertyModel(parent)

        x = yaml.load(PROJECT_SETTINGS)
        self.project_setting_model.load_settings(x, params_dict)

        self.ui.property_epub.setModel(self.project_setting_model)
        epub_item = self.project_setting_model.get("Epub Settings")
        self.ui.property_epub.setRootIndex(epub_item.index())

        # self.python_combo = PythonComboButton(self._parent)
        #
        # self.ui.project_info_form_layout.addRow(
        #     self.tr("Python Interpreter"),
        #     self.python_combo,
        # )
        #
        self.ui.edit_extension_button.clicked.connect(self.edit_extensions)

    def setup(self, project_item):
        # type: (ProjectItem) -> None
        if project_item and project_item.is_valid():
            self.ui.label_project.setText(project_item.project())
            self.ui.label_path.setText(project_item.path())
            self.ui.project_tool_widget.setEnabled(True)

            venv = project_item.venv_setting()
            if venv:
                self.ui.label_interpreter.setText(venv.python_path())
            else:
                self.ui.label_interpreter.setText(sys_env.default_env().python_path())
        else:
            self.ui.label_project.clear()
            self.ui.label_interpreter.clear()
            self.ui.project_tool_widget.setEnabled(False)
            return

        self.ui.list_widget_extensions.clear()

        for ext_name in project_item.settings.extensions:
            self.ui.list_widget_extensions.addItem(ext_name)

    def edit_extensions(self):
        dlg = ExtensionDialog(self._parent)
        dlg.exec_()


# noinspection PyArgumentList
class ExtensionDialog(QDialog):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(ExtensionDialog, self).__init__(parent)
        self.widget = QWidget(self)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self
        )

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.widget)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

        self.ui = Ui_Form()
        self.ui.setupUi(self.widget)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)


class ExtensionTreeWidget(QTreeWidget):
    def addExtension(self, name):
        item = QTreeWidgetItem([name])
        item.setCheckState(0, Qt.Checked)
        self.addTopLevelItem(item)
    pass
