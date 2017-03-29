#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals
import os
import platform
import subprocess

from PySide.QtCore import *
from PySide.QtGui import *

from . import icon
from .main_window_ui import Ui_MainWindow
from .project_list_model import ProjectListModel, ProjectItem
from .quickstart import QuickStartDialog
from . import quickstart_wizard
from . import extension
from . import editor
from .util.exec_sphinx import launch
from .settings import SettingsDialog, Settings
from . import sphinx_value_types


SETTING_DIR = ".sphinx-explorer"
SETTINGS_TOML = "settings.toml"


# from .theme_dialog import ThemeDialog
# from .sphinx_analyzer import SphinxInfo


class MainWindow(QMainWindow):
    JSON_NAME = "setting.json"

    def __init__(self, sys_dir, home_dir, parent=None):
        super(MainWindow, self).__init__(parent)

        # make setting dir
        self.setting_dir = home_dir
        if not os.path.isdir(self.setting_dir):
            os.makedirs(self.setting_dir)
        self.settings = Settings(os.path.join(self.setting_dir, SETTINGS_TOML))

        # load extension
        sphinx_value_types.init()
        extension.init(os.path.join(sys_dir, "extension_plugin"))
        editor.init(os.path.join(sys_dir, "editor_plugin"))

        # create actions
        self.del_document_act = QAction("Delete Document", self)
        self.del_document_act.setIcon(icon.load("remove"))
        self.del_document_act.setShortcut(QKeySequence.Delete)
        self.del_document_act.setShortcutContext(Qt.WidgetShortcut)
        self.del_document_act.setObjectName("action_del_document")

        self.open_act = QAction(icon.load("editor"), "Open Editor", self, triggered=self._open_dir)
        self.show_act = QAction(icon.load("open_folder"), "Show File", self, triggered=self._show_directory)
        self.terminal_act = QAction(icon.load("terminal"), "Open Terminal", self, triggered=self._open_terminal)
        self.auto_build_act = QAction(icon.load("reload"), "Auto Build", self)

        self.editor_acts = []
        for name, ed in editor.editors():
            act = QAction(ed.name, self)
            act.setIcon(ed.icon)
            self.editor_acts.append(act)

        # setup ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.project_list_model = ProjectListModel(parent=self)

        # setup editor menu
        for act in self.editor_acts:
            self.ui.menu_editor.addAction(act)

        # setup icon
        self.ui.tool_button_quick_start.setIcon(icon.load("rocket"))
        self.ui.action_quickstart.setIcon(icon.load("rocket"))
        self.ui.action_add_document.setIcon(icon.load("plus"))
        self.ui.action_settings.setIcon(icon.load("setting"))
        self.ui.action_wizard.setIcon(icon.load("magic"))

        # setup tool button
        self.ui.tool_add_document.setDefaultAction(self.ui.action_add_document)
        self.ui.tool_setting.setDefaultAction(self.ui.action_settings)

        # setup quick start menu
        self.quick_start_menu = QMenu(self)
        self.quick_start_menu.addAction(self.ui.action_wizard)
        self.quick_start_menu.addAction(self.ui.action_quickstart)
        self.ui.tool_button_quick_start.setMenu(self.quick_start_menu)
        self.ui.tool_button_quick_start.setPopupMode(QToolButton.InstantPopup)

        # setup project tree view
        self.ui.tree_view_projects.addAction(self.del_document_act)
        self.ui.tree_view_projects.setIndentation(0)
        self.ui.tree_view_projects.setHeaderHidden(True)
        self.ui.tree_view_projects.setModel(self.project_list_model)
        self.ui.tree_view_projects.resizeColumnToContents(0)
        self.project_selection_model = self.ui.tree_view_projects.selectionModel()
        self.project_selection_model.currentChanged.connect(self.onProjectCurrentChanged)

        # setup property view
        self.ui.table_view_property.setReadOnly(True)

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

    def _setup(self):
        self.project_list_model.load(self.settings.projects)

    def _save(self):
        self.settings.dump(self.project_list_model.dump())

    def _create_context_menu(self, item, doc_path):
        # type : (ProjectItem, str) -> QMenu
        menu = QMenu(self)

        if not item.can_make():
            self.auto_build_act.setEnabled(False)

        self.open_act.setData(doc_path)
        self.show_act.setData(doc_path)
        self.terminal_act.setData(doc_path)

        # Warning: don't use lambda to connect!!
        # Process finished with exit code -1073741819 (0xC0000005) ...
        #
        # open_act.triggered.connect(lambda: self.editor.open_dir(doc_path))
        # show_act.triggered.connect(self._show_directory)
        # terminal_act.triggered.connect(lambda: self._open_terminal(doc_path))

        menu.addAction(self.open_act)
        menu.addAction(self.show_act)
        menu.addAction(self.terminal_act)
        menu.addAction(self.auto_build_act)
        menu.addAction(self.del_document_act)

        return menu

    def closeEvent(self, evt):
        self._save()
        super(MainWindow, self).closeEvent(evt)

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
        if not path:
            return

        path = os.path.normpath(path)
        if platform.system() == "Windows":
            cmd = ["explorer", path]
        elif platform.system() == "Darwin":
            cmd = ["open", path]
        else:
            cmd = ["xdg-open", path]

        launch(" ".join(cmd), path)

    def _open_terminal(self):
        # type: (str) -> None
        path = self.sender().data()
        if not path:
            return

        if platform.system() == "Windows":
            subprocess.Popen("cmd", cwd=os.path.normpath(path))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", os.path.normpath(path)])
        else:
            subprocess.Popen("gnome-terminal", cwd=os.path.normpath(path))

    @Slot()
    def on_action_settings_triggered(self):
        dlg = SettingsDialog(self)
        dlg.setup(self.settings.default_values)
        if dlg.exec_() == QDialog.Accepted:
            self.settings.default_values.update(dlg.settings())

    @Slot(QModelIndex, QModelIndex)
    def onProjectCurrentChanged(self, current, _):
        # type: (QModelIndex, QModelIndex) -> None
        self._setup_property_widget(current)

    @Slot(QModelIndex)
    def onSphinxInfoLoaded(self, index):
        # type: (QModelIndex) -> None
        if self.ui.tree_view_projects.currentIndex() == index:
            self._setup_property_widget(index)

    @Slot()
    def on_action_quickstart_triggered(self):
        dlg = QuickStartDialog(self.settings.default_values, self)
        if dlg.exec_() == QDialog.Accepted:
            print(dlg.dump())
            pass

    @Slot()
    def on_action_wizard_triggered(self):
        quickstart_wizard.main(self.settings.default_values, self)

    @Slot()
    def on_action_add_document_triggered(self):
        # noinspection PyCallByClass
        doc_dir = QFileDialog.getExistingDirectory(
            self,
            "add document",
            os.path.join(self.setting_dir, "..")
        )

        if doc_dir:
            self.project_list_model.add_document(doc_dir)

    @Slot()
    def on_action_del_document_triggered(self):
        indexes = self.ui.tree_view_projects.selectedIndexes()

        if indexes:
            # noinspection PyCallByClass
            result = QMessageBox.question(
                self,
                self.windowTitle(),
                "Delete Document?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if result != QMessageBox.Yes:
                return

            for index in sorted(indexes, key=lambda x: x.row()):
                self.project_list_model.takeRow(index.row())

    @Slot(QModelIndex)
    def on_tree_view_projects_doubleClicked(self, index):
        # type: (QModelIndex) -> None
        if index.isValid():
            path = self.project_list_model.path(index)
            self.settings.editor().open_dir(path)

    @Slot(QPoint)
    def on_tree_view_projects_customContextMenuRequested(self, pos):
        # type: (QPoint) -> None
        index = self.ui.tree_view_projects.indexAt(pos)
        if index.isValid():
            path = os.path.normpath(self.project_list_model.path(index))
            item = self.project_list_model.rowItem(index)
            menu = self._create_context_menu(item, path)
            menu.exec_(self.ui.tree_view_projects.viewport().mapToGlobal(pos))

    @staticmethod
    def _auto_build(path):
        # type: (str) -> None
        """
        sphinx - autobuild
        docs
        docs / _build / html
        """
        pass

    def _setup_property_widget(self, index):
        # type: (QModelIndex) -> None
        widget = self.ui.table_view_property
        widget.clear()

        if not index.isValid():
            return

        item = self.project_list_model.item(index.row())     # type: ProjectItem
        if item is None or item.info is None or not item.info.is_valid():
            return

        conf = item.info.conf
        widget.add_property(None, "project", conf.get("project"))
        widget.add_property(None, "author", conf.get("author"))
        widget.add_property(None, "version", conf.get("version"))
        widget.add_property(None, "release", conf.get("release"))

        widget.add_category("Information")
        widget.add_property(None, "html_theme", conf.get("html_theme"))

        widget.add_category("Extensions")
        for ex_name in conf.get("extensions", []):
            widget.add_property(None, ex_name, "Yes")

        widget.resizeColumnToContents(0)
