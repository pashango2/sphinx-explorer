#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from collections import OrderedDict

import toml
from PySide.QtCore import *
from PySide.QtGui import *

from . import icon
from .property_widget import PropertyWidget, find_value_type
from .quickstart_dialog_ui import Ui_Dialog
from . import extension
from .util.exec_sphinx import quote


TOML_PATH = "settings/quickstart.toml"


def exec_(cmd, text_edit, parent):
    process = QProcess(parent)

    process.start(cmd)
    return process


def cmd(d):
    # type: (dict) -> basestring
    ignore_params = ["project", "prefix", "path", "version", "release"]
    arrow_extension = [
        "ext-autodoc",
        "ext-doctest",
        "ext-intersphinx",
        "ext-todo",
        "ext-coverage",
        "ext-imgmath",
        "ext-mathjax",
        "ext-ifconfig",
        "ext-viewcode",
    ]

    opts = []
    for key, value in d.items():
        if key in ignore_params or not value:
            continue

        if key == "html_theme":
            opts.append("-d " + key + "=" + quote(value))
            continue

        if key.startswith("ext-") and key not in arrow_extension:
            continue

        if value is True:
            opts.append("--" + key)
        else:
            opts.append("--" + key + "=" + quote(value))

    return " ".join([
        "sphinx-quickstart",
        "-q",
        "-p " + quote(d["project"]),
        "-a " + quote(d["author"]),
        "-v " + quote(d["version"]),
        "-r " + quote(d["release"]) if d.get("release") else "",
     ] + opts + [quote(d["path"])])


_questions = None


def get_questions():
    global _questions
    if _questions is None:
        _questions = Questions(TOML_PATH)
    return _questions


def quickstart_settings():
    return toml.load(TOML_PATH, OrderedDict)


def _property_iter(params):
    if "extensions" in params:
        for ext_name in params["extensions"]:
            value_dict = extension.get(ext_name)
            if value_dict is None:
                value_dict = {
                    "default": True,
                }

            value_dict["name"] = ext_name
            value_dict["value_type"] = "TypeBool"

            yield ext_name, value_dict
    else:
        for param_key, value_dict in params.items():
            yield param_key, value_dict


class Questions(object):
    def __init__(self, setting_path):
        self.settings = toml.load(setting_path, OrderedDict)

        self._property_map = {}
        for category in self.categories():
            for key, param in self.properties(category).items():
                self._property_map[key] = param

    def property(self, keys):
        for key in keys:
            yield self._property_map[key]

    def items(self, widget, keys):
        for key in keys:
            param = self._property_map[key]
            yield widget.create_property(
                key, {
                    "name": param.get("name"),
                    "description": param.get("description"),
                    "value_type": param.get("value_type"),
                }
            )

    def categories(self):
        return self.settings.keys()

    def properties(self, category=None):
        if category is None:
            params = OrderedDict()
            for category in self.categories():
                params[category] = self.properties(category)
            return params
        else:
            params = self.settings[category]

            if "extensions" in params:
                new_params = OrderedDict()
                for ext_name in params["extensions"]:
                    value_dict = extension.get(ext_name)
                    if value_dict is None:
                        value_dict = OrderedDict({
                            "default": True,
                        })

                    value_dict["name"] = ext_name
                    value_dict["value_type"] = "TypeBool"

                    new_params[ext_name] = value_dict

                params = new_params

            return params


def property_item_iter(property_widget, params, enables=None):
    item_dict = {}
    for param_key, value_dict in _property_iter(params):
        if enables and param_key not in enables:
            continue

        item = property_widget.create_property(
            param_key,
            value_dict.get("name"),
            None,
            value_dict.get("description"),
            find_value_type(value_dict.get("value_type")),
        )

        if value_dict.get("description"):
            item.setToolTip(value_dict.get("description").strip())

        item_dict[param_key] = item
        yield item

    for param_key, value_dict in _property_iter(params):
        if enables and param_key not in enables:
            continue
        item = item_dict[param_key]

        if value_dict.get("link") and value_dict["link"] in item_dict:
            item.set_link(item_dict[value_dict["link"]], value_dict.get("link_format"))


class QuickStartDialog(QDialog):
    def __init__(self, default_settings, parent=None):
        # type: (dict, QWidget or None) -> None
        super(QuickStartDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        questions = get_questions()

        property_widget = self.ui.table_view_property
        property_widget.load_settings(questions.properties(), default_settings)

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

    def dump(self):
        return self.ui.table_view_property.dump()

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
