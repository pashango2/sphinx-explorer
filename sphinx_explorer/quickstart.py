#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
from PySide.QtGui import *
from PySide.QtCore import *
import os
import toml
from .quickstart_dialog_ui import Ui_Dialog
from collections import OrderedDict, namedtuple
from .property_widget import TypeBool, TypeDirPath, AllTypes
from .property_widget.value_types import TypeLanguage
from .theme_dialog import TypeHtmlTheme
from . import icon


TOML_PATH = "settings/quickstart.toml"


class QuickStartDialog(QDialog):
    def __init__(self, parent=None):
        """
        :type parent: QWidget
        """
        super(QuickStartDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        questions = toml.load(TOML_PATH, OrderedDict)

        property_widget = self.ui.table_view_property
        for category, params in questions.items():
            property_widget.add_category(category)

            for param_key, value_dict in params.items():
                item = property_widget.add_property(
                    param_key,
                    value_dict.get("name"),
                    value_dict.get("default"),
                    self._find_value_type(value_dict.get("value_type")),
                )

                if value_dict.get("description"):
                    item.setToolTip(value_dict.get("description").strip())

        property_widget.resizeColumnsToContents()
        property_widget.setAlternatingRowColors(True)
        property_widget.setStyleSheet("alternate-background-color: #2b2b2b;")

        # action
        self.ui.action_bookmark.setIcon(icon.load("bookmark"))
        self.ui.action_export.setIcon(icon.load("export"))
        self.ui.action_import.setIcon(icon.load("import"))

        self.ui.tool_bookmark.setDefaultAction(self.ui.action_bookmark)
        self.ui.tool_export.setDefaultAction(self.ui.action_export)
        self.ui.tool_import.setDefaultAction(self.ui.action_import)

    @staticmethod
    def _find_value_type(type_name):
        for value_type in AllTypes + [TypeHtmlTheme]:
            if value_type.__name__ == type_name:
                return value_type
        return None

    @Slot()
    def on_action_export_triggered(self):
        dlg = ImportExportDialog(False, self)
        dlg.set_text(self.ui.table_view_property.dumps())
        dlg.exec_()

    @Slot()
    def on_action_import_triggered(self):
        dlg = ImportExportDialog(True, self)
        if dlg.exec_() == QDialog.Accepted:
            self.ui.table_view_property.loads(dlg.text())


class ImportExportDialog(QDialog):
    def __init__(self, import_flag, parent=None):
        super(ImportExportDialog, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.text_box = QPlainTextEdit(self)

        if import_flag:
            button_flag = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        else:
            button_flag = QDialogButtonBox.Ok
        self.button_box = QDialogButtonBox(button_flag, parent=self)

        self.layout.addWidget(self.text_box)
        self.layout.addWidget(self.button_box)

        font = QFont(self.text_box.font())
        font.setPointSize(font.pointSize() + 1)
        self.text_box.setFont(font)

        # noinspection PyUnresolvedReferences
        self.button_box.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.button_box.rejected.connect(self.reject)

        if import_flag:
            self.setWindowTitle("Import")
        else:
            self.setWindowTitle("Export")
            self.text_box.setReadOnly(True)

    def set_text(self, text):
        # type: (str) -> None
        self.text_box.setPlainText(text)

    def text(self):
        # type: () -> str
        return self.text_box.toPlainText()
