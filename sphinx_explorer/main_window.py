#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import ctypes
import os
import platform
import webbrowser
from collections import OrderedDict
import logging

import toml
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from six import PY2

from sphinx_explorer import python_venv
from sphinx_explorer.ui.main_window_ui import Ui_MainWindow
from sphinx_explorer.util import icon
from . import plugin
from . import property_widget
from . import sphinx_value_types
from . import package_mgr
from .project_list_model import ProjectListModel, ProjectItem
from .dialogs import ProjectSettingDialog
from .system_settings import SystemSettingsDialog, SystemSettings
from .task import SystemInitTask, push_task
from .util.commander import commander
from .wizard import quickstart_wizard
from . import about

SETTING_DIR = ".sphinx-explorer"
SETTINGS_TOML = "settings.toml"


# noinspection PyArgumentList
class MainWindow(QMainWindow):
    JSON_NAME = "setting.json"

    if PY2:
        def tr(self, *args):
            return super(MainWindow, self).tr(str(args[0]))

    def _act(self, icon_name, name, triggered=None):
        if icon_name:
            return QAction(icon.load(icon_name), name, self, triggered=triggered)
        else:
            return QAction(name, self, triggered=triggered)

    def __init__(self, sys_dir, home_dir, parent=None):
        super(MainWindow, self).__init__(parent)
        self.wizard_path = os.path.join(sys_dir, "settings")

        # load plugin
        plugin.init(self)
        plugin.load_plugin(os.path.join(sys_dir, "settings"))
        plugin.load_plugin(home_dir)

        # make setting dir
        self.setting_dir = home_dir
        if not os.path.isdir(self.setting_dir):
            os.makedirs(self.setting_dir)
        self.settings = SystemSettings(os.path.join(self.setting_dir, SETTINGS_TOML))

        # setting value types
        sphinx_value_types.init()

        # setup params dict
        toml_path = os.path.join(self.wizard_path, "params.toml")
        self.params_dict = toml.load(toml_path, OrderedDict)

        for ext_name, ext in plugin.extension.list_iter():
            self.params_dict[ext_name] = {
                "value_type": "TypeCheck",
                "default": True,
                "description": ext.description,
                "description_path": ext.ext_path,
            }

        # create actions
        self.open_act = self._act("editor", self.tr("Open Editor"), self._open_dir)
        self.show_act = self._act("open_folder", self.tr("Open Directory"), self._show_directory)
        self.terminal_act = self._act("terminal", self.tr("Open Terminal"), self._open_terminal)
        self.auto_build_act = self._act("reload", self.tr("Auto Build"), self._auto_build)
        self.update_apidoc_act = self._act("update", self.tr("Update sphinx-apidoc"), self._update_apidoc)
        self.open_html_act = self._act("chrome", self.tr("Open browser"), self._open_browser)
        self.copy_path_act = self._act("clippy", self.tr("Copy Path"), self._on_copy_path)
        self.project_setting_act = self._act("setting", self.tr("Project Setting"), self._project_setting)

        self.close_act = self._act(None, self.tr("Exit"), self.close)
        self.make_html_act = self._act(None, self.tr("HTML"), self._on_make_html)
        self.make_epub_act = self._act(None, self.tr("Epub"), self._on_make_epub)
        self.make_latex_pdf_act = self._act(None, self.tr("LaTex PDF"), self._on_make_latex_pdf)
        self.make_clean_act = self._act(None, self.tr("Clean"), self._on_make_clean)

        # setup ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # setup logger
        self.gui_logger = GuiLogger(self)
        self.gui_logger.edit = self.ui.text_edit_error
        logging.getLogger().addHandler(self.gui_logger)

        # create models
        self.project_list_model = ProjectListModel(parent=self)

        # setup file menu
        self.ui.menuFile_F.addSeparator()
        self.ui.menuFile_F.addAction(self.close_act)

        # setup icon
        self.ui.action_add_document.setIcon(icon.load("plus"))
        self.ui.action_settings.setIcon(icon.load("setting"))
        self.ui.action_wizard.setIcon(icon.load("magic"))
        self.ui.action_move_up.setIcon(icon.load("arrow_up"))
        self.ui.action_move_down.setIcon(icon.load("arrow_down"))
        self.ui.action_delete_document.setIcon(icon.load("remove"))

        self.make_html_act.setIcon(icon.load("html5"))
        self.make_epub_act.setIcon(icon.load("epub"))
        self.make_latex_pdf_act.setIcon(icon.load("pdf"))
        self.make_clean_act.setIcon(icon.load("eraser"))

        # setup tool button
        self.ui.button_add.setDefaultAction(self.ui.action_add_document)
        self.ui.button_up.setDefaultAction(self.ui.action_move_up)
        self.ui.button_down.setDefaultAction(self.ui.action_move_down)
        self.ui.button_del.setDefaultAction(self.ui.action_delete_document)

        self.ui.action_delete_document.setShortcut(QKeySequence.Delete)
        self.ui.action_delete_document.setShortcutContext(Qt.WidgetShortcut)
        self.ui.action_move_up.setShortcutContext(Qt.WidgetShortcut)
        self.ui.action_move_down.setShortcutContext(Qt.WidgetShortcut)
        self.copy_path_act.setShortcut(QKeySequence.Copy)
        self.copy_path_act.setShortcutContext(Qt.WidgetShortcut)

        # connect
        self.ui.action_reload.triggered.connect(self.reload)

        # setup project tree view
        self.ui.tree_view_projects.addAction(self.ui.action_move_up)
        self.ui.tree_view_projects.addAction(self.ui.action_move_down)
        self.ui.tree_view_projects.addAction(self.ui.action_delete_document)
        self.ui.tree_view_projects.addAction(self.ui.action_reload)
        self.ui.tree_view_projects.addAction(self.copy_path_act)

        self.ui.tree_view_projects.setIndentation(0)
        self.ui.tree_view_projects.setModel(self.project_list_model)
        self.ui.tree_view_projects.resizeColumnToContents(0)
        self.projects_selection_model = self.ui.tree_view_projects.selectionModel()

        self.projects_selection_model.currentChanged.connect(self._on_project_changed)

        # setup project model
        self.project_list_model.projectLoaded.connect(self.onProjectLoaded)

        # setup context menu
        self.ui.tree_view_projects.setContextMenuPolicy(Qt.CustomContextMenu)

        # setup toolbar
        self.ui.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

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

        # setup project tool frame
        self.ui.project_tool_layout.setAlignment(Qt.AlignLeft)
        self.add_tool_action(self.make_clean_act)
        self.add_tool_action(None)
        self.add_tool_action(self.make_html_act)
        self.add_tool_action(self.make_epub_act)
        self.add_tool_action(self.make_latex_pdf_act)
        self.add_tool_action(None)
        self.add_tool_action(self.open_act)
        self.add_tool_action(self.show_act)
        self.add_tool_action(self.terminal_act)
        self.add_tool_action(self.open_html_act)
        self.add_tool_action(self.auto_build_act)
        self.add_tool_action(None)
        self.add_tool_action(self.project_setting_act)

        # set icon
        # TODO: This is Feature Support.
        # ProjectTools.set_file_icons(
        #     folder_icon=icon.load("folder"),
        #     file_icon=icon.load("file_text")
        # )

        property_widget.set_icon(
            add_icon=icon.load("plus"),
            up_icon=icon.load("arrow_up"),
            down_icon=icon.load("arrow_down"),
            delete_icon=icon.load("remove"),
            cog_icon=icon.load("cog"),
            open_dir_icon=icon.load("open_folder"),
        )

        python_venv.ICON_DICT["sys"] = icon.load("python")
        python_venv.ICON_DICT["anaconda"] = icon.load("anaconda")
        python_venv.ICON_DICT["venv"] = icon.load("python")

        # system init task
        task = SystemInitTask(self.settings, self)
        task.messaged.connect(self._on_task_message)
        task.checkPythonEnvFinished.connect(self._on_check_python_env_finished)
        task.checkPythonPackageFinished.connect(self._on_check_python_package_finished)
        task.checkLatestPackageFinished.connect(self._on_check_latest_package_finished)

        push_task(task)

        self.update_icon()

        # setup end
        self.setAcceptDrops(True)
        self._setup()
        self.ui.tree_view_projects.setFocus()

    def update_icon(self):
        self.open_act.setIcon(self.settings.editor_icon())

    def add_tool_action(self, action):
        layout = self.ui.project_tool_layout

        if action:
            button = QToolButton(self)
            button.setDefaultAction(action)
            layout.addWidget(button)
        else:
            v_line = QFrame(self)
            v_line.setFrameShape(QFrame.VLine)
            layout.addWidget(v_line)

    @Slot(str)
    def output_error(self, err_msg):
        self.ui.text_edit_error.append(err_msg)
        self.ui.output_tab_widget.setCurrentIndex(1)

    def _on_task_message(self, msg, timeout=3000):
        self.ui.statusbar.showMessage(msg, timeout)

    @staticmethod
    def _on_check_python_env_finished(env):
        python_venv.setup(env)

    @staticmethod
    def _on_check_python_package_finished(python_env, packages):
        model = package_mgr.get_model(python_env)
        model.load(packages)

    @staticmethod
    def _on_check_latest_package_finished(python_env, packages):
        model = package_mgr.get_model(python_env)
        model.update(packages)

    def _setup(self):
        self.project_list_model.load(self.settings.projects)

        # load layout
        layout = QSettings(os.path.join(self.setting_dir, "layout.ini"), QSettings.IniFormat)
        if layout:
            if layout.value("geometry"):
                self.restoreGeometry(layout.value("geometry"))

            if layout.value("windowState"):
                self.restoreState(layout.value("windowState"))

    def _save(self):
        self.settings.dump(self.project_list_model.dump())

        # save layout
        layout = QSettings(os.path.join(self.setting_dir, "layout.ini"), QSettings.IniFormat)
        layout.setValue("geometry", self.saveGeometry())
        layout.setValue("windowState", self.saveState())

    def _create_context_menu(self, item, doc_path):
        # type : (ProjectItem, str) -> QMenu
        menu = QMenu(self)

        self.auto_build_act.setEnabled(item.can_make())
        can_apidoc = item.can_apidoc()

        self.open_act.setData(doc_path)
        self.show_act.setData(doc_path)
        self.terminal_act.setData(doc_path)
        self.update_apidoc_act.setData(item.index() if can_apidoc else None)
        self.auto_build_act.setData(item.index())
        self.make_html_act.setData(item.index())
        self.open_html_act.setData(item.index())

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

        make_menu = QMenu(self)
        make_menu.addAction(self.make_html_act)
        make_menu.addAction(self.make_epub_act)
        make_menu.addAction(self.make_latex_pdf_act)
        make_menu.addSeparator()
        make_menu.addAction(self.make_clean_act)

        make_menu.setTitle("Make")
        menu.addMenu(make_menu)

        menu.addSeparator()

        if can_apidoc:
            menu.addAction(self.update_apidoc_act)

        menu.addAction(self.open_html_act)
        menu.addAction(self.auto_build_act)
        menu.addSeparator()
        menu.addAction(self.copy_path_act)
        menu.addAction(self.ui.action_delete_document)
        menu.addSeparator()
        menu.addAction(self.project_setting_act)

        return menu

    def closeEvent(self, evt):
        self._save()
        self.ui.plain_output.terminate()
        QThreadPool.globalInstance().clear()
        QThreadPool.globalInstance().waitForDone(0)
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
        index = self.ui.tree_view_projects.currentIndex()
        item = self.project_list_model.itemFromIndex(index)
        if item:
            self.settings.editor().open_dir(item.path())

    def _show_directory(self):
        # type: () -> None
        index = self.ui.tree_view_projects.currentIndex()
        item = self.project_list_model.itemFromIndex(index)
        if item:
            commander.show_directory(item.path())

    def _open_terminal(self):
        # type: () -> None
        index = self.ui.tree_view_projects.currentIndex()
        item = self.project_list_model.itemFromIndex(index)
        if item:
            commander.open_terminal(item.path())

    def _on_make_html(self):
        # type: () -> None
        self._make("html", self.ui.tree_view_projects.currentIndex())

    def _on_make_epub(self):
        # type: () -> None
        self._make("epub", self.ui.tree_view_projects.currentIndex())

    def _on_make_latex_pdf(self):
        # type: () -> None
        self._make("latexpdf", self.ui.tree_view_projects.currentIndex())

    def _on_make_clean(self):
        # type: () -> None
        self._make("clean", self.ui.tree_view_projects.currentIndex())

    def _make(self, make_cmd, index, callback=None):
        if index and index.isValid():
            project_item = self.project_list_model.itemFromIndex(index)
        else:
            return

        cwd = project_item.path()
        venv_setting = project_item.venv_setting() or self.settings.venv_setting()
        venv_cmd = [
            python_venv.activate_command(venv_setting, cwd),
            commander.make_command(make_cmd, cwd)
        ]
        venv_cmd = [x for x in venv_cmd if x]

        self.ui.plain_output.exec_command(
            commander(cmds=venv_cmd),
            cwd,
            clear=True,
            callback=callback
        )

    def _project_setting(self):
        current = self.ui.tree_view_projects.currentIndex()
        item = self.project_list_model.itemFromIndex(current)
        if item:
            dlg = ProjectSettingDialog(self.params_dict, item, self)
            dlg.exec_()

    def _on_project_changed(self, current, _):
        # type: (QModelIndex, QModelIndex) -> None
        item = self.project_list_model.itemFromIndex(current)
        self.setup_project_settings(item)

    def setup_project_settings(self, item):
        # type: (ProjectItem) -> None
        if item and item.is_valid():
            self.ui.label_project.setText(item.project())
            self.ui.label_path.setText(item.path())
            self.ui.project_tool_widget.setEnabled(True)
        else:
            self.ui.label_project.clear()

            self.ui.project_tool_widget.setEnabled(False)

    def _auto_build(self):
        # type: () -> None
        index = self.ui.tree_view_projects.currentIndex()
        if not index.isValid():
            return

        item = self.project_list_model.itemFromIndex(index)  # type: ProjectItem
        if item:
            commander.console(
                item.auto_build_command(),
                os.path.normpath(item.path())
            )

    def _update_apidoc(self):
        # type: () -> None
        index = self.ui.tree_view_projects.currentIndex()
        if not index.isValid():
            return

        item = self.project_list_model.itemFromIndex(index)  # type: ProjectItem
        if item:
            self.ui.plain_output.clear()
            cmd, cwd = item.update_apidoc_command()
            if cmd:
                self.ui.plain_output.exec_command(cmd, cwd)

    def _open_browser(self):
        # type: () -> None
        index = self.ui.tree_view_projects.currentIndex()
        if not index.isValid():
            return

        item = self.project_list_model.itemFromIndex(index)  # type: ProjectItem
        if item:
            if not item.has_html():
                html_path = item.html_path()
                if html_path:
                    self._make("html", index, lambda: webbrowser.open(html_path))
            else:
                html_path = item.html_path()
                if os.path.isfile(html_path):
                    webbrowser.open(html_path)

    def _on_copy_path(self):
        index = self.ui.tree_view_projects.currentIndex()
        path = self.project_list_model.path(index)
        if path:
            # noinspection PyArgumentList
            clipboard = QApplication.clipboard()
            clipboard.setText(path)

    @Slot()
    def on_action_settings_triggered(self):
        dlg = SystemSettingsDialog(self)
        dlg.setup(self.setting_dir, self.settings, self.params_dict)
        if dlg.exec_() == QDialog.Accepted:
            dlg.update_settings(self.settings)

    @Slot()
    def on_action_about_qt_triggered(self):
        # noinspection PyCallByClass,PyTypeChecker
        QMessageBox.aboutQt(self, self.tr("About Qt"))

    @Slot()
    def on_action_about_triggered(self):
        # noinspection PyCallByClass
        QMessageBox.about(
            self,
            self.tr("About Sphinx Explorer"),
            about.message
        )

    @Slot(QModelIndex)
    def onProjectLoaded(self, index):
        # type: (QModelIndex) -> None
        # self.ui.tree_view_projects.resizeColumnToContents(0)
        pass

    @Slot()
    def on_action_wizard_triggered(self):
        # () -> None
        wizard = quickstart_wizard.create_wizard(
            plugin.template_model,
            self.params_dict,
            self.settings.default_values,
            self
        )
        wizard.addDocumentRequested.connect(self.add_document)
        wizard.exec_()

    @Slot(str)
    def add_document(self, path):
        item = self.project_list_model.add_document(path)
        if item:
            self.ui.tree_view_projects.setCurrentIndex(item.index())

    @Slot()
    def on_action_add_document_triggered(self):
        # () -> None
        default_path = os.path.join(self.setting_dir, "..")

        # noinspection PyCallByClass,PyTypeChecker
        doc_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Add document"),
            self.settings.default_root_path(default_path),
        )

        if doc_dir:
            self.project_list_model.add_document(doc_dir)

    @Slot()
    def on_action_delete_document_triggered(self):
        # () -> None
        indexes = self.ui.tree_view_projects.selectedIndexes()
        indexes = [x for x in indexes if x.column() == 0]

        if indexes:
            # noinspection PyCallByClass,PyTypeChecker
            result = QMessageBox.question(
                self,
                self.windowTitle(),
                self.tr("Remove the document from list?"),
                QMessageBox.Yes | QMessageBox.No,
            )
            if result == QMessageBox.Yes:
                for index in sorted(indexes, key=lambda idx: idx.row(), reverse=True):
                    self.project_list_model.takeRow(index.row())

    def _move(self, up_flag):
        # type: (bool) -> None
        indexes = self.ui.tree_view_projects.selectedIndexes()
        indexes = [index for index in indexes if index.column() == 0]
        if indexes:
            indexes.sort(key=lambda x: x.row(), reverse=not up_flag)

            selection_model = self.ui.tree_view_projects.selectionModel()
            selection = QItemSelection()

            stop_idx = -1 if up_flag else self.project_list_model.rowCount()
            first_item = None

            for index in indexes:
                item = self.project_list_model.itemFromIndex(index)
                first_item = first_item or item
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

                selection.select(item.index(), item.index().sibling(item.row(), 1))

            selection_model.select(
                selection,
                QItemSelectionModel.ClearAndSelect
            )
            selection_model.setCurrentIndex(first_item.index(), QItemSelectionModel.SelectCurrent)

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
                commander.show_directory(path)

    @Slot(QPoint)
    def on_tree_view_projects_customContextMenuRequested(self, pos):
        # type: (QPoint) -> None
        index = self.ui.tree_view_projects.indexAt(pos)
        if index.isValid():
            path = os.path.normpath(self.project_list_model.path(index))
            item = self.project_list_model.rowItem(index)
            menu = self._create_context_menu(item, path)
            menu.exec_(self.ui.tree_view_projects.viewport().mapToGlobal(pos))


class GuiLogger(logging.Handler):
    def __init__(self, main_window):
        super(GuiLogger, self).__init__()
        self.main_window = main_window

    def emit(self, record):
        self.main_window.output_error(self.format(record))
