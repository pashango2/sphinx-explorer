#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import toml
from collections import OrderedDict
from PySide.QtGui import *
from .settings_ui import Ui_Form
from .property_widget import TypeChoice
from .sphinx_value_types import TypeLanguage, TypeHtmlTheme
from . import editor
from .quickstart import questions
import locale


class Settings(OrderedDict):
    def __init__(self, setting_path):
        super(Settings, self).__init__()
        self._setting_path = setting_path

        # noinspection PyBroadException
        try:
            self.update(self.load())
        except:
            self.setup_default()

    def setup_default(self):
        self["default_values"] = {
            "editor": "atom",
            "language": Settings.default_locale(),
        }
        self["projects"] = {"projects": []}

    @property
    def default_values(self):
        return self["default_values"]

    @property
    def projects(self):
        return self["projects"]["projects"]

    @staticmethod
    def default_locale():
        language = locale.getdefaultlocale()[0]
        if language:
            return language.split("_")[0].lower()
        return None

    def load(self):
        return toml.load(open(self._setting_path), OrderedDict)

    def dump(self, projects):
        self["projects"] = {"projects": projects}
        return toml.dump(self, open(self._setting_path, "w"))

    def default_editor(self):
        return self.get("editor", "atom")

    def set_default_editor(self, editor_name):
        self["editor"] = editor_name

    def editor(self):
        # type: () -> editor.Editor
        return editor.get(self.default_editor())


class SettingsDialog(QDialog):
    DEFAULT_SETTING_KEYS = [
        "author",
        "language",
        "html_theme",
        "sep",
    ]

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.widget = QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.widget)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        # noinspection PyUnresolvedReferences
        self._buttons.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self._buttons.rejected.connect(self.reject)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.layout.addWidget(self._buttons)

        self.setLayout(self.layout)

        self.setWindowTitle("Settings")
        self.resize(1000, 600)

    def setup(self, settings):
        # type: (Settings) -> None
        widget = self.ui.property_widget

        items = []
        for name, ed in editor.editors():
            items.append({
                "text": ed.name,
                "value": name,
                "icon": ed.icon,
            })

        editor_choice = TypeChoice(items)
        widget.add_property(
            "editor",
            "Editor",
            settings.default_editor(),
            value_type=editor_choice
        )

        widget.add_category("Default values")
        default_values = settings.default_values
        for item in questions(default_values, self.DEFAULT_SETTING_KEYS):
            widget.add_property_item(item)

        widget.resizeColumnToContents(0)


    def update_settings(self, settings):
        # type: (Settings) -> None
        param = self.ui.property_widget.dump()

        default_param = {
            key: value
            for key, value in param.items()
            if key in self.DEFAULT_SETTING_KEYS
        }
        settings.default_values.update(default_param)

        settings.set_default_editor(param["editor"])


