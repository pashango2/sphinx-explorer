#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
import os
import platform
import subprocess

from PySide.QtCore import *
from PySide.QtGui import *

from editor_plugin import atom_editor
from . import icon
from .main_window_ui import Ui_MainWindow
from .project_list_model import ProjectListModel
from .property_widget import PropertyWidget
from .quickstart import QuickStartDialog
from . import quickstart_wizard


# from .theme_dialog import ThemeDialog
# from .sphinx_analyzer import SphinxInfo


class MainWindow(QMainWindow):
    JSON_NAME = "setting.json"

    def __init__(self, home_dir, parent=None):
        super(MainWindow, self).__init__(parent)

        # create actions
        self.del_document_act = QAction("Delete Document", self)
        self.del_document_act.setIcon(icon.load("remove"))
        self.del_document_act.setShortcut(QKeySequence.Delete)
        self.del_document_act.setShortcutContext(Qt.WidgetShortcut)
        self.del_document_act.setObjectName("action_del_document")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.home_dir = home_dir
        self.editor = atom_editor

        self.project_list_model = ProjectListModel(parent=self)

        self.ui.tool_button_quick_start.setIcon(icon.load("rocket"))
        self.ui.action_quickstart.setIcon(icon.load("rocket"))
        self.ui.action_add_document.setIcon(icon.load("plus"))
        self.ui.action_setting.setIcon(icon.load("setting"))
        self.ui.action_wizard.setIcon(icon.load("magic"))

        # self.ui.tool_button_quick_start.setDefaultAction(self.ui.action_quickstart)
        self.ui.tool_add_document.setDefaultAction(self.ui.action_add_document)
        self.ui.tool_setting.setDefaultAction(self.ui.action_setting)

        self.ui.tree_view_projects.addAction(self.del_document_act)

        # setup project tree view
        self.ui.tree_view_projects.setIndentation(0)

        # setup context menu
        self.ui.tree_view_projects.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setAcceptDrops(True)

        self._setup()

        self.ui.tree_view_projects.setModel(self.project_list_model)
        self.ui.tree_view_projects.resizeColumnToContents(0)

        self.ui.tree_view_projects.setFocus()

        self.quick_start_menu = QMenu(self)
        self.quick_start_menu.addAction(self.ui.action_wizard)
        self.quick_start_menu.addAction(self.ui.action_quickstart)

        self.ui.tool_button_quick_start.setMenu(self.quick_start_menu)
        self.ui.tool_button_quick_start.setPopupMode(QToolButton.InstantPopup)

        # move to center
        r = self.geometry()
        r.moveCenter(QApplication.desktop().availableGeometry().center())
        self.setGeometry(r)

    def _setup(self):
        if not os.path.isdir(self.home_dir):
            os.makedirs(self.home_dir)

        json_path = os.path.join(self.home_dir, self.JSON_NAME)

        if os.path.isfile(json_path):
            load_object = json.load(open(json_path))

            if "projects" in load_object and load_object["projects"]:
                self.project_list_model.load(load_object["projects"])

        self._setup_property_widget(self.ui.table_view_property)

    def _save(self):
        json_path = os.path.join(self.home_dir, self.JSON_NAME)

        dump_object = {
            "projects": self.project_list_model.dump()
        }
        json.dump(dump_object, open(json_path, "w"))

    def _create_context_menu(self, item, doc_path):
        # type : (ProjectItem, str) -> QMenu
        menu = QMenu(self)

        open_act = QAction(icon.load("editor"), "Open Editor", menu)
        show_act = QAction(icon.load("open_folder"), "Show File", menu)
        terminal_act = QAction(icon.load("terminal"), "Open Terrminal", menu)
        auto_build_act = QAction(icon.load("reload"), "Auto Build", menu)

        if not item.can_make():
            auto_build_act.setEnabled(False)

        # noinspection PyUnresolvedReferences
        open_act.triggered.connect(lambda: self.editor.open(doc_path))
        # noinspection PyUnresolvedReferences
        show_act.triggered.connect(lambda: self._show_directory(doc_path))
        # noinspection PyUnresolvedReferences
        terminal_act.triggered.connect(lambda: self._open_terminal(doc_path))

        menu.addAction(open_act)
        menu.addAction(show_act)
        menu.addAction(terminal_act)
        menu.addAction(auto_build_act)
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

    @staticmethod
    def _show_directory(path):
        # type: (str) -> None
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", os.path.normpath(path)])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", os.path.normpath(path)])
        else:
            subprocess.Popen(["xdg-open", os.path.normpath(path)])

    @staticmethod
    def _open_terminal(path):
        # type: (str) -> None
        if platform.system() == "Windows":
            subprocess.Popen(["cmd", "/k cd", os.path.normpath(path)])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", os.path.normpath(path)])
        else:
            subprocess.Popen(["gnome-terminal", os.path.normpath(path)])

    @Slot()
    def on_action_quickstart_triggered(self):
        dlg = QuickStartDialog(self)
        dlg.exec_()
        # dlg = ThemeDialog(self)
        # dlg.exec_()

    @Slot()
    def on_action_wizard_triggered(self):
        quickstart_wizard.main(self)

    @Slot()
    def on_action_add_document_triggered(self):
        # noinspection PyCallByClass
        doc_dir = QFileDialog.getExistingDirectory(
            self,
            "add document",
            os.path.join(self.home_dir, "..")
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
            self.editor.open(path)

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

    def _setup_property_widget(self, widget):
        # type: (PropertyWidget) -> None
        # widget.add_category("カテゴリA")
        # widget.add_property("path", "Path", "kita-", TypeDirPath)
        # widget.add_property("Project", "kita-")
        # widget.add_property("Author", "kita-")
        # widget.add_property("Version", "kita-")
        # widget.add_property("Release", "kita-")
        #
        # widget.add_category("カテゴリB")
        # widget.add_property("Sep", True, TypeBool)
        # # widget.add_property("extensions", "test", ValueTypes.TypeStrList)
        pass



