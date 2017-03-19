#! coding:utf-8
import os
import json
import platform
import subprocess

from PySide.QtCore import *
from PySide.QtGui import *

from sphinx_explorer.editor_plugin import atom_editor
from . import quickstart
from . import icon
from .main_window_ui import Ui_MainWindow
from .project_list_model import ProjectListModel


class MainWindow(QMainWindow):
    JSON_NAME = "setting.json"

    def __init__(self, home_dir, parent=None):
        super(MainWindow, self).__init__(parent)

        # create actions
        self.del_document_act = QAction("Delete Document", self)
        self.del_document_act.setShortcut(QKeySequence.Delete)
        self.del_document_act.setShortcutContext(Qt.WidgetShortcut)
        self.del_document_act.setObjectName("action_del_document")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.home_dir = home_dir
        self.editor = atom_editor

        self.project_list_model = ProjectListModel(parent=self)

        self.ui.action_quickstart.setIcon(icon.load("plus"))
        self.ui.action_add_document.setIcon(icon.load("plus"))

        self.ui.tool_button_quick_start.setDefaultAction(self.ui.action_quickstart)
        self.ui.tool_add_document.setDefaultAction(self.ui.action_add_document)

        self.ui.tree_view_projects.addAction(self.del_document_act)

        # setup context menu
        self.ui.tree_view_projects.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setAcceptDrops(True)

        self._setup()

        self.ui.tree_view_projects.setModel(self.project_list_model)

    def _setup(self):
        try:
            os.makedirs(self.home_dir)
        except FileExistsError:
            pass

        json_path = os.path.join(self.home_dir, self.JSON_NAME)

        if os.path.isfile(json_path):
            load_object = json.load(open(json_path))

            if "projects" in load_object:
                self.project_list_model.load(load_object["projects"])

    def _save(self):
        json_path = os.path.join(self.home_dir, self.JSON_NAME)

        dump_object = {
            "projects": self.project_list_model.dump()
        }
        json.dump(dump_object, open(json_path, "w"))

    def _create_context_menu(self, doc_path):
        # type : (str) -> QMenu
        menu = QMenu(self)

        open_act = QAction(icon.load("editor"), "Open Editor", menu)
        show_act = QAction(icon.load("open_folder"), "Show File", menu)
        auto_build_act = QAction(icon.load("reload"), "Auto Build", menu)

        # noinspection PyUnresolvedReferences
        open_act.triggered.connect(lambda: self.editor.open(doc_path))
        # noinspection PyUnresolvedReferences
        show_act.triggered.connect(lambda: self._show_directory(doc_path))

        menu.addAction(open_act)
        menu.addAction(show_act)
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
        print(urls)
        dirs = [x for x in urls if os.path.isdir(x)]

        for doc_path in dirs:
            index = self.project_list_model.find(doc_path)
            if index.isValid() is False:
                self.project_list_model.add_document(doc_path)

    @staticmethod
    def _show_directory(path):
        # type: (str) -> None
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    @Slot()
    def on_action_quickstart_triggered(self):
        dlg = quickstart.QuickStartDialog(self)
        dlg.exec_()

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
            indexes = sorted(indexes, key=lambda x: x.row())

            for index in indexes:
                self.project_list_model.takeRow(index.row())

    @Slot(QModelIndex)
    def on_tree_view_projects_doubleClicked(self, index):
        # type: (QModelIndex) -> None
        if index.isValid():
            path = index.data()

            self.editor.open(path)

    @Slot(QPoint)
    def on_tree_view_projects_customContextMenuRequested(self, pos):
        # type: (QPoint) -> None
        index = self.ui.tree_view_projects.indexAt(pos)
        if index.isValid():
            menu = self._create_context_menu(index.data())
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
