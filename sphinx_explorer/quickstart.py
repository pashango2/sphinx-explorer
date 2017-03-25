#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from collections import OrderedDict

import toml
from PySide.QtCore import *
from PySide.QtGui import *

from . import icon
from .property_widget import AllTypes
from .quickstart_dialog_ui import Ui_Dialog
from .theme_dialog import TypeHtmlTheme

TOML_PATH = "settings/quickstart.toml"


def quickstart_settings():
    return toml.load(TOML_PATH, OrderedDict)


class QuickStartDialog(QDialog):
    def __init__(self, parent=None):
        # type: (QWidget or None) -> None
        super(QuickStartDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        questions = quickstart_settings()

        property_widget = self.ui.table_view_property
        for category, params in questions.items():
            property_widget.add_category(category)

            for param_key, value_dict in params.items():
                item = property_widget.add_property(
                    param_key,
                    value_dict.get("name"),
                    value_dict.get("default"),
                    value_dict.get("description"),
                    self.find_value_type(value_dict.get("value_type")),
                )

                if value_dict.get("description"):
                    item.setToolTip(value_dict.get("description").strip())

        property_widget.resizeColumnsToContents()
        property_widget.setAlternatingRowColors(True)
        property_widget.setStyleSheet("alternate-background-color: #2b2b2b;")

        # actions
        self.ui.action_bookmark.setIcon(icon.load("bookmark"))
        self.ui.action_export.setIcon(icon.load("export"))
        self.ui.action_import.setIcon(icon.load("import"))

        self.ui.tool_bookmark.setDefaultAction(self.ui.action_bookmark)
        self.ui.tool_export.setDefaultAction(self.ui.action_export)
        self.ui.tool_import.setDefaultAction(self.ui.action_import)

        self.ui.table_view_property.setFocus()

    @staticmethod
    def find_value_type(type_name):
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

    @Slot()
    def on_action_bookmark_triggered(self):
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.TextInput)
        dlg.setWindowFlags(Qt.Popup)
        geometry = self.ui.tool_bookmark.geometry()
        pos = self.ui.tool_bookmark.mapToGlobal(geometry.bottomLeft())
        dlg.setGeometry(QRect(pos, QSize(200, 100)))
        dlg.setLabelText("Bookmark")
        dlg.setTextValue("test")
        dlg.exec_()


class BookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super(BookmarkDialog, self).__init__(parent)

        self.line_edit = QLineEdit(self)
        self.add_button = QPushButton("Add", self)
        self.cancel_button = QPushButton("Cancel", self)

        self.form_layout = QFormLayout()
        self.form_layout.addWidget(QLabel("Bookmark"))
        self.form_layout.addRow("Name", self.line_edit)


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
