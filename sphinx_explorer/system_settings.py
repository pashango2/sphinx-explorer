#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import locale
import logging
import os
from collections import OrderedDict

import toml
# noinspection PyPackageRequirements
import yaml
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from sphinx_explorer import python_venv
from sphinx_explorer.sphinx_value_types.pages import PythonInterpreterWidget
from sphinx_explorer.ui.settings_ui import Ui_Form
from sphinx_explorer.util import icon
from .plugin import extension, editor
from .property_widget import TypeChoice, PropertyModel
from .util.commander import commander

logger = logging.getLogger(__name__)


class SystemSettings(OrderedDict):
    def __init__(self, setting_path):
        super(SystemSettings, self).__init__()
        self._setting_path = setting_path

        # noinspection PyBroadException
        try:
            data = self.load()
            self.update(data)
        except FileNotFoundError:
            self.setup_default()
        except:
            logger.error("read setting file failed.")
            self.setup_default()

    def setup_default(self):
        self["Default Values"] = {
            "language": SystemSettings.default_locale(),
            "path": os.path.expanduser('~'),
        }
        self["projects"] = {"projects": []}
        self["Editor"] = {
            "editor": editor.check_exist() or editor.DEFAULT_EDITOR
        }

    def default_root_path(self, default_path):
        return self["Default Values"].get("path") or default_path

    @property
    def default_values(self):
        if self["Default Values"].get("language") is None:
            self["Default Values"]["language"] = SystemSettings.default_locale()
        return self["Default Values"]

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

    def venv_setting(self):
        try:
            env = self["Python Interpreter"].get("python")
            return python_venv.VenvSetting(env)
        except KeyError:
            return python_venv.VenvSetting()


class CategoryFilterModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().itemFromIndex(source_index)

        return item and item.is_category

    def itemFromIndex(self, index):
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)

    def columnCount(self, *_):
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
    label: Editor
- "#*Default Values":
    label: Default Values
-
    - path
    - author
    - language
    - html_theme
    - sep

- "#*Python Interpreter"
-
    - python
- "#*Extensions":
    label: Extensions
"""


class SystemSettingsDialog(QDialog):
    DEFAULT_SETTING_KEYS = [
        "path",
        "author",
        "language",
        "html_theme",
        "sep",
    ]

    # noinspection PyArgumentList
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
            self
        )

        self.open_setting_dir_button = QPushButton(self)
        self.open_setting_dir_button.setText(self.tr("Open Setting Directory"))

        self.layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.open_setting_dir_button)
        self.h_layout.addWidget(self._buttons)
        self.layout.addWidget(self.widget)
        self.layout.addLayout(self.h_layout)
        self.setLayout(self.layout)

        self.setWindowTitle(self.tr(str("SystemSettings")))
        self.resize(1000, 600)

        # self._setup_category()
        self.ui.tree_view_category.setModel(self.category_model)
        self.category_selection_model = self.ui.tree_view_category.selectionModel()

        # setup buttons
        self.open_setting_dir_button.setIcon(icon.load("open_folder"))

        self._connect()

    # noinspection PyUnresolvedReferences
    def _connect(self):
        self.open_setting_dir_button.clicked.connect(self.on_button_open_home_dir_clicked)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

    def on_button_open_home_dir_clicked(self):
        if self.home_dir:
            commander.show_directory(self.home_dir)

    def _on_category_changed(self, current, _):
        item = self.category_model.itemFromIndex(current)
        if item:
            if item.key == "Extensions":
                self.ui.stacked_widget.setCurrentIndex(1)
            elif item.key == "Python Interpreter":
                if self.ui.stacked_widget.count() == 2:
                    widget = PythonInterpreterWidget(self)
                    root_item = self.property_model.get(item.tree_key())
                    widget.setup(self.property_model, root_item.index())
                    self.ui.stacked_widget.addWidget(widget)
                self.ui.stacked_widget.setCurrentIndex(2)
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

        # setup extension
        self.setup_extensions()

        self.ui.property_widget.set_values(settings)
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
                "value_type": editor_choice
            }
        )

        self.setup_extensions()

    def update_settings(self, settings):
        # type: (SystemSettings) -> None
        param = self.ui.property_widget.dump(exclude_default=True)
        settings.update(param)
