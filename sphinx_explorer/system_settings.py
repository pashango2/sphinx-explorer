#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import locale
from collections import OrderedDict

import toml
import yaml
from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer.plugin import editor
from .property_widget import TypeChoice, PropertyModel
from .plugin import extension
from .settings_ui import Ui_Form
from . import icon
from .util.exec_sphinx import show_directory
import logging

logger = logging.getLogger(__name__)


class SystemSettings(OrderedDict):
    def __init__(self, setting_path):
        super(SystemSettings, self).__init__()
        self._setting_path = setting_path

        # noinspection PyBroadException
        try:
            self.update(self.load())
        except:
            self.setup_default()

    def setup_default(self):
        self["default_values"] = {
            "language": SystemSettings.default_locale(),
        }
        self["projects"] = {"projects": []}
        self["editor"] = "atom"

    def default_root_path(self, default_path):
        return self["default_values"].get("path") or default_path

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
        editor_name = self.get("Editor", {}).get("editor")
        return editor.default_editor(editor_name)

    def set_default_editor(self, editor_name):
        self.setdefault("Editor", {})["editor"] = editor_name

    def editor(self):
        # type: () -> editor.Editor
        return editor.get(self.default_editor())

    def editor_icon(self):
        # type: () -> QIcon
        return self.editor().icon if self.editor() else QIcon()

    def venv_info(self):
        return None


class CategoryModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(CategoryModel, self).__init__(parent)


class CategoryFilterModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().itemFromIndex(source_index)

        return item and item.is_category

    def itemFromIndex(self, index):
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)

    def columnCount(self, _):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundColorRole:
            return None
        elif role == Qt.ForegroundRole:
            return None

        return super(CategoryFilterModel, self).data(index, role)

    def flags(self, index):
        return (
            Qt.ItemIsSelectable | Qt.ItemIsEnabled

        )


SYSTEM_SETTINGS = """
- "#*Editor":
    - label: Editor
- "#*Default Values":
    - label: Default Values
-
    - path
    - author
    - language
    - html_theme
    - sep

- "#*Extensions":
    - label: Extensions
"""


class SystemSettingsDialog(QDialog):
    DEFAULT_SETTING_KEYS = [
        "path",
        "author",
        "language",
        "html_theme",
        "sep",
    ]

    def __init__(self, parent=None):
        super(SystemSettingsDialog, self).__init__(parent)
        self.widget = QWidget(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self.widget)

        self.ui.splitter.setStretchFactor(1, 1)
        self.ui.splitter.setSizes([310, 643])

        self.settings = None
        self.home_dir = None
        self.params_dict = {}

        self.property_model = PropertyModel(self)
        self.category_model = CategoryFilterModel(self)
        self.category_model.setSourceModel(self.property_model)
        self.ui.property_widget.setModel(self.property_model)

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

        self.setWindowTitle(self.tr(str("SystemSettings")))
        self.resize(1000, 600)

        # self._setup_category()
        self.ui.tree_view_category.setModel(self.category_model)
        self.category_selection_model = self.ui.tree_view_category.selectionModel()

        # setup buttons
        self.ui.button_open_home_dir.setIcon(icon.load("open_folder"))
        self.ui.button_open_home_dir.clicked.connect(self.on_button_open_home_dir_clicked)

    @Slot()
    def on_button_open_home_dir_clicked(self):
        if self.home_dir:
            show_directory(self.home_dir)

    def _on_category_changed(self, current, _):
        item = self.category_model.itemFromIndex(current)
        if item:
            if item.key == "Extensions":
                self.ui.stacked_widget.setCurrentIndex(1)
            else:
                self.ui.stacked_widget.setCurrentIndex(0)
                root_item = self.property_model.get(item.tree_key())
                self.ui.property_widget.setRootIndex(root_item.index())
                self.ui.property_widget.setup()
                self.ui.property_widget.resizeColumnToContents(0)

    def setup(self, home_dir, settings, params_dict):
        self.settings = settings
        self.home_dir = home_dir
        self.params_dict = params_dict

        d = yaml.load(SYSTEM_SETTINGS)
        self.property_model.required_flag = False
        self.property_model.load_settings(d, params_dict)

        editor_item = self.property_model.get("Editor")
        if not editor_item:
            logger.warning("editor item don't find.")
            return

        items = []
        for name, ed in editor.editors():
            items.append({
                "text": ed.name,
                "value": name,
                "icon": ed.icon,
            })

        editor_choice = TypeChoice(items)
        editor_item.add_property(
            "editor",
            settings.default_editor(),
            params={
                "name": "Editor",
                "value_type": editor_choice
            },
        )

        # setup default values
        item = self.property_model.get("Default Values")
        item.set_values(settings.get("default_values"))

        # setup extension
        self.setup_extensions()

        self.ui.property_widget.setup()

        self.ui.tree_view_category.expandAll()

        first_index = self.category_model.index(0, 0)
        self.category_selection_model.select(first_index, QItemSelectionModel.Select)
        self.category_selection_model.currentChanged.connect(self._on_category_changed)

    def setup_extensions(self):
        # type: () -> None
        parent_item = self.property_model.get("Extensions")

        for ext_name, ext in extension.extensions():
            if ext.has_setting_params():
                category = parent_item.add_category("#*" + ext_name, ext_name)

                for param_name, params in ext.setting_params:
                    category.add_property(
                        param_name,
                        params=params
                    )

    def setup_Settings(self):
        # type: () -> None
        widget = self.ui.property_widget
        settings = self.settings

        # setup editor
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
            {
                "name": "Editor",
                "value": settings.default_editor(),
                "value_type": editor_choice
            }
        )

        # setup defaut values
        item = widget.get("Default Values")
        item.set_values(settings.default_values())

        self.setup_extensions()

    def update_settings(self, settings):
        # type: (SystemSettings) -> None
        param = self.ui.property_widget.dump()

        default_param = {
            key: value
            for key, value in param.items()
            if key in self.DEFAULT_SETTING_KEYS
        }
        settings.default_values.update(default_param)
        print(param)
        settings.set_default_editor(param["Editor"]["editor"])
