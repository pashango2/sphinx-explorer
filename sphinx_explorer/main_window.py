#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import toml
import fnmatch
import webbrowser
import platform
import ctypes
from collections import OrderedDict

from PySide.QtCore import *
from PySide.QtGui import *
from six import string_types

from sphinx_explorer.wizard import quickstart_wizard, apidoc_wizard
from . import editor
from . import extension
from . import icon
from . import sphinx_value_types
from .main_window_ui import Ui_MainWindow
from .project_list_model import ProjectListModel, ProjectItem
from .settings import SettingsDialog, Settings
from .util.exec_sphinx import launch, console, show_directory, open_terminal
from .template_model import TemplateModel

if False:
    from typing import Iterator

SETTING_DIR = ".sphinx-explorer"
SETTINGS_TOML = "settings.toml"


class MainWindow(QMainWindow):
    JSON_NAME = "setting.json"

    def __init__(self, sys_dir, home_dir, parent=None):
        super(MainWindow, self).__init__(parent)
        self.template_model = TemplateModel(self)
        self.wizard_path = os.path.join(sys_dir, "settings")

        # make setting dir
        self.setting_dir = home_dir
        if not os.path.isdir(self.setting_dir):
            os.makedirs(self.setting_dir)
        self.settings = Settings(os.path.join(self.setting_dir, SETTINGS_TOML))

        # load extension
        self._load_plugin(sys_dir)

        # setup params dict
        toml_path = os.path.join(self.wizard_path, "params.toml")
        self.params_dict = toml.load(toml_path, OrderedDict)

        for ext_name, ext in extension.list_iter():
            self.params_dict[ext_name] = {
                "value_type": "TypeBool",
                "default": True
            }

        # create actions
        self.open_act = QAction(icon.load("editor"), "Open Editor", self, triggered=self._open_dir)
        self.show_act = QAction(icon.load("open_folder"), "Show File", self, triggered=self._show_directory)
        self.terminal_act = QAction(icon.load("terminal"), "Open Terminal", self, triggered=self._open_terminal)
        self.auto_build_act = QAction(icon.load("reload"), "Auto Build", self, triggered=self._auto_build)
        self.apidoc_act = QAction(icon.load("update"), "Update sphinx-apidoc", self, triggered=self._apidoc)
        self.open_html_act = QAction(icon.load("chrome"), "Open browser", self, triggered=self._open_browser)
        self.close_act = QAction("Exit", self, triggered=self.close)

        self.editor_acts = []
        for name, ed in editor.editors():
            act = QAction(ed.name, self)
            act.setIcon(ed.icon)
            self.editor_acts.append(act)

        # setup ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.project_list_model = ProjectListModel(parent=self)
        self.project_list_model.autoBuildRequested.connect(self.onAutoBuildRequested)

        # setup file menu
        self.ui.menuFile_F.addSeparator()
        self.ui.menuFile_F.addAction(self.close_act)

        # setup icon
        self.ui.tool_button_quick_start.setIcon(icon.load("book"))
        self.ui.action_add_document.setIcon(icon.load("plus"))
        self.ui.action_settings.setIcon(icon.load("setting"))
        self.ui.action_wizard.setIcon(icon.load("magic"))
        self.ui.action_apidoc.setIcon(icon.load("book"))
        self.ui.action_move_up.setIcon(icon.load("arrow_up"))
        self.ui.action_move_down.setIcon(icon.load("arrow_down"))
        self.ui.action_delete_document.setIcon(icon.load("remove"))

        # setup tool button
        self.ui.tool_setting.setDefaultAction(self.ui.action_settings)
        self.ui.button_add.setDefaultAction(self.ui.action_add_document)
        self.ui.button_up.setDefaultAction(self.ui.action_move_up)
        self.ui.button_down.setDefaultAction(self.ui.action_move_down)
        self.ui.button_del.setDefaultAction(self.ui.action_delete_document)

        self.ui.action_delete_document.setShortcutContext(Qt.WidgetShortcut)
        self.ui.action_move_up.setShortcutContext(Qt.WidgetShortcut)
        self.ui.action_move_down.setShortcutContext(Qt.WidgetShortcut)

        # connect
        self.ui.action_reload.triggered.connect(self.reload)

        # setup quick start menu
        self.quick_start_menu = QMenu(self)
        self.quick_start_menu.addAction(self.ui.action_wizard)
        self.quick_start_menu.addAction(self.ui.action_apidoc)
        self.ui.tool_button_quick_start.setMenu(self.quick_start_menu)
        self.ui.tool_button_quick_start.setPopupMode(QToolButton.InstantPopup)

        # setup project tree view
        self.ui.tree_view_projects.addAction(self.ui.action_move_up)
        self.ui.tree_view_projects.addAction(self.ui.action_move_down)
        self.ui.tree_view_projects.addAction(self.ui.action_delete_document)
        self.ui.tree_view_projects.addAction(self.ui.action_reload)

        self.ui.tree_view_projects.setIndentation(0)
        self.ui.tree_view_projects.setHeaderHidden(True)
        self.ui.tree_view_projects.setModel(self.project_list_model)
        self.ui.tree_view_projects.resizeColumnToContents(0)

        # setup project model
        self.project_list_model.sphinxInfoLoaded.connect(self.onSphinxInfoLoaded)

        # setup context menu
        self.ui.tree_view_projects.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setAcceptDrops(True)
        self._setup()
        self.ui.tree_view_projects.setFocus()

        # move to center
        r = self.geometry()
        # noinspection PyArgumentList
        r.moveCenter(QApplication.desktop().availableGeometry().center())
        self.setGeometry(r)

        # set icon
        if platform.system() == "Windows":
            # noinspection PyBroadException
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sphinx Explorer")
            except:
                pass

        self.setWindowIcon(icon.load("sphinx"))

    def _setup(self):
        self.project_list_model.load(self.settings.projects)

    def _save(self):
        self.settings.dump(self.project_list_model.dump())

    def _load_plugin(self, sys_dir):
        # type: (string_types) -> None
        sphinx_value_types.init()
        extension.init(os.path.join(sys_dir, "plugin", "extension"))

        editor_dir = os.path.join(sys_dir, "plugin", "editor")
        editor.init()
        for file_path in self._walk_files(editor_dir, "*.toml"):
            editor.load_plugin(file_path)

        wizard_dir = os.path.join(sys_dir, "plugin", "wizard")
        for toml_path in self._walk_files(wizard_dir, "*.toml"):
            self.template_model.load_plugin(toml_path)

    @staticmethod
    def _walk_files(dir_path, ext):
        # type: (string_types, string_types) -> Iterator[string_types]
        for root, _, files in os.walk(dir_path):
            for file_path in fnmatch.filter(files, ext):
                yield os.path.join(root, file_path)

    def _create_context_menu(self, item, doc_path):
        # type : (ProjectItem, str) -> QMenu
        menu = QMenu(self)

        self.auto_build_act.setEnabled(item.can_make())
        can_apidoc = item.can_apidoc()

        self.open_act.setIcon(self.settings.editor_icon())

        self.open_act.setData(doc_path)
        self.show_act.setData(doc_path)
        self.terminal_act.setData(doc_path)
        self.apidoc_act.setData(item.index() if can_apidoc else None)
        self.auto_build_act.setData(item.index())
        self.open_html_act.setData(item.index())

        self.open_html_act.setEnabled(item.has_html())
        # Warning: don't use lambda to connect!!
        # Process finished with exit code -1073741819 (0xC0000005) ...
        #
        # open_act.triggered.connect(lambda: self.editor.open_dir(doc_path))
        # show_act.triggered.connect(self._show_directory)
        # terminal_act.triggered.connect(lambda: self._open_terminal(doc_path))

        menu.addAction(self.open_act)
        menu.addAction(self.show_act)
        menu.addAction(self.terminal_act)

        menu.addSeparator()
        if can_apidoc:
            menu.addAction(self.apidoc_act)

        menu.addAction(self.open_html_act)
        menu.addAction(self.auto_build_act)
        menu.addSeparator()
        menu.addAction(self.ui.action_delete_document)

        return menu

    def closeEvent(self, evt):
        self._save()
        self.ui.plain_output.terminate()
        super(MainWindow, self).closeEvent(evt)

    def event(self, evt):
        if evt.type() == QEvent.WindowActivate:
            self.reload()

        return super(MainWindow, self).event(evt)

    def reload(self):
        self.project_list_model.update_items()

    def dragEnterEvent(self, evt):
        if evt.mimeData().hasFormat("text/uri-list"):
            evt.acceptProposedAction()

    def dropEvent(self, evt):
        urls = [x.toLocalFile() for x in evt.mimeData().urls()]
        dirs = [x for x in urls if os.path.isdir(x)]

        for doc_path in dirs:
            self.project_list_model.add_document(doc_path)

    def _open_dir(self):
        # type: () -> None
        path = self.sender().data()
        if not path:
            return
        self.settings.editor().open_dir(path)

    def _show_directory(self):
        # type: () -> None
        path = self.sender().data()
        if path:
            show_directory(path)

    def _open_terminal(self):
        # type: () -> None
        path = self.sender().data()
        if path:
            open_terminal(path)

    def _auto_build(self):
        # type: () -> None
        index = self.sender().data()
        if not index.isValid():
            return

        item = self.project_list_model.itemFromIndex(index)  # type: ProjectItem
        if item:
            console(item.auto_build_command(), os.path.normpath(item.path()))

    def _open_browser(self):
        # type: () -> None
        index = self.sender().data()
        if not index.isValid():
            return

        item = self.project_list_model.itemFromIndex(index)  # type: ProjectItem
        if item:
            html_path = item.html_path()
            if os.path.isfile(html_path):
                webbrowser.open(html_path)

    def _apidoc(self):
        # type: () -> None
        index = self.sender().data()
        if not index.isValid():
            return

        item = self.project_list_model.itemFromIndex(index)  # type: ProjectItem
        if item:
            self.ui.plain_output.clear()
            item.apidoc_update(self.ui.plain_output)

    @Slot(str, ProjectItem)
    def onAutoBuildRequested(self, cmd, _):
        # self.ui.plain_output.exec_command(cmd)
        launch(cmd)

    @Slot()
    def on_action_settings_triggered(self):
        dlg = SettingsDialog(self)
        dlg.setup(self.settings, self.params_dict)
        if dlg.exec_() == QDialog.Accepted:
            dlg.update_settings(self.settings)

    @Slot(QModelIndex)
    def onSphinxInfoLoaded(self, index):
        # type: (QModelIndex) -> None
        pass

    @Slot()
    def on_action_wizard_triggered(self):
        # () -> None
        # quickstart_wizard.main(self.settings.default_values, self.add_document, self)
        wizard = quickstart_wizard.create_wizard(self.params_dict, self.settings.default_values, self)
        if wizard.exec_() == QDialog.Accepted:
            self.add_document(wizard.path())

    @Slot()
    def on_action_apidoc_triggered(self):
        # () -> None
        wizard = apidoc_wizard.create_wizard(self.params_dict, self.settings.default_values, self)
        if wizard.exec_() == QDialog.Accepted:
            self.add_document(wizard.path())

    @Slot(str)
    def add_document(self, path):
        item = self.project_list_model.add_document(path)
        if item:
            self.ui.tree_view_projects.setCurrentIndex(item.index())

    @Slot()
    def on_action_add_document_triggered(self):
        # () -> None
        default_path = os.path.join(self.setting_dir, "..")

        # noinspection PyCallByClass
        doc_dir = QFileDialog.getExistingDirectory(
            self,
            "add document",
            self.settings.default_root_path(default_path),
        )

        if doc_dir:
            self.project_list_model.add_document(doc_dir)

    @Slot()
    def on_action_delete_document_triggered(self):
        # () -> None
        indexes = self.ui.tree_view_projects.selectedIndexes()

        if indexes:
            # noinspection PyCallByClass
            result = QMessageBox.question(
                self,
                self.windowTitle(),
                "Delete Document?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if result == QMessageBox.Yes:
                for index in sorted(indexes, key=lambda x: x.row(), reverse=True):
                    self.project_list_model.takeRow(index.row())

    def _move(self, up_flag):
        # type: (bool) -> None
        indexes = self.ui.tree_view_projects.selectedIndexes()
        if indexes:
            indexes.sort(key=lambda x: x.row(), reverse=not up_flag)

            selection_model = self.ui.tree_view_projects.selectionModel()
            selection = QItemSelection()

            stop_idx = -1 if up_flag else self.project_list_model.rowCount()

            for index in indexes:
                item = self.project_list_model.itemFromIndex(index)
                if up_flag:
                    insert_row = item.row() - 1
                    movable = stop_idx < insert_row
                else:
                    insert_row = item.row() + 1
                    movable = insert_row < stop_idx

                if movable:
                    self.project_list_model.takeRow(item.row())
                    self.project_list_model.insertRow(insert_row, item)
                else:
                    stop_idx = item.row()

                selection.select(item.index(), item.index())

            selection_model.select(
                selection,
                QItemSelectionModel.ClearAndSelect
            )

    @Slot()
    def on_action_move_up_triggered(self):
        # () -> None
        self._move(True)

    @Slot()
    def on_action_move_down_triggered(self):
        # () -> None
        self._move(False)

    @Slot(QModelIndex)
    def on_tree_view_projects_doubleClicked(self, index):
        # type: (QModelIndex) -> None
        if index.isValid():
            path = self.project_list_model.path(index)
            if path:
                show_directory(path)

    @Slot(QPoint)
    def on_tree_view_projects_customContextMenuRequested(self, pos):
        # type: (QPoint) -> None
        index = self.ui.tree_view_projects.indexAt(pos)
        if index.isValid():
            path = os.path.normpath(self.project_list_model.path(index))
            item = self.project_list_model.rowItem(index)
            menu = self._create_context_menu(item, path)
            menu.exec_(self.ui.tree_view_projects.viewport().mapToGlobal(pos))
