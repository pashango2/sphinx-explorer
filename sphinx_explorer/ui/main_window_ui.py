# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/program/sphinx-explorer/sphinx_explorer/ui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1019, 797)
        self.project_tool_widget = QtWidgets.QWidget(MainWindow)
        self.project_tool_widget.setObjectName("project_tool_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.project_tool_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.project_tool_layout = QtWidgets.QHBoxLayout()
        self.project_tool_layout.setObjectName("project_tool_layout")
        self.verticalLayout.addLayout(self.project_tool_layout)
        self.tab_widget = QtWidgets.QTabWidget(self.project_tool_widget)
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tab_widget.setObjectName("tab_widget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.project_info_form_layout = QtWidgets.QFormLayout()
        self.project_info_form_layout.setObjectName("project_info_form_layout")
        self.label_project_2 = QtWidgets.QLabel(self.tab)
        self.label_project_2.setObjectName("label_project_2")
        self.project_info_form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_project_2)
        self.label_project = QtWidgets.QLabel(self.tab)
        self.label_project.setText("")
        self.label_project.setObjectName("label_project")
        self.project_info_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_project)
        self.label_path_2 = QtWidgets.QLabel(self.tab)
        self.label_path_2.setObjectName("label_path_2")
        self.project_info_form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_path_2)
        self.label_path = QtWidgets.QLabel(self.tab)
        self.label_path.setText("")
        self.label_path.setObjectName("label_path")
        self.project_info_form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_path)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.project_info_form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox = QtWidgets.QComboBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.project_info_form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.verticalLayout_7.addLayout(self.project_info_form_layout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.edit_extension_button = QtWidgets.QToolButton(self.tab)
        self.edit_extension_button.setObjectName("edit_extension_button")
        self.horizontalLayout.addWidget(self.edit_extension_button)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.list_widget_extensions = QtWidgets.QListWidget(self.tab)
        self.list_widget_extensions.setObjectName("list_widget_extensions")
        self.verticalLayout_7.addWidget(self.list_widget_extensions)
        self.tab_widget.addTab(self.tab, "")
        self.auto_class = QtWidgets.QWidget()
        self.auto_class.setObjectName("auto_class")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.auto_class)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tab_widget.addTab(self.auto_class, "")
        self.epub = QtWidgets.QWidget()
        self.epub.setObjectName("epub")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.epub)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.property_epub = PropertyWidget(self.epub)
        self.property_epub.setObjectName("property_epub")
        self.verticalLayout_9.addWidget(self.property_epub)
        self.tab_widget.addTab(self.epub, "")
        self.verticalLayout.addWidget(self.tab_widget)
        MainWindow.setCentralWidget(self.project_tool_widget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1019, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile_F = QtWidgets.QMenu(self.menubar)
        self.menuFile_F.setObjectName("menuFile_F")
        self.menuCreate_C = QtWidgets.QMenu(self.menubar)
        self.menuCreate_C.setObjectName("menuCreate_C")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dock_outputs = QtWidgets.QDockWidget(MainWindow)
        self.dock_outputs.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dock_outputs.setObjectName("dock_outputs")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.output_tab_widget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.output_tab_widget.setTabPosition(QtWidgets.QTabWidget.South)
        self.output_tab_widget.setObjectName("output_tab_widget")
        self.Output = QtWidgets.QWidget()
        self.Output.setObjectName("Output")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.Output)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.plain_output = QConsoleWidget(self.Output)
        self.plain_output.setObjectName("plain_output")
        self.verticalLayout_4.addWidget(self.plain_output)
        self.output_tab_widget.addTab(self.Output, "")
        self.Error = QtWidgets.QWidget()
        self.Error.setObjectName("Error")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.Error)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.text_edit_error = QtWidgets.QTextEdit(self.Error)
        self.text_edit_error.setObjectName("text_edit_error")
        self.verticalLayout_5.addWidget(self.text_edit_error)
        self.output_tab_widget.addTab(self.Error, "")
        self.verticalLayout_2.addWidget(self.output_tab_widget)
        self.dock_outputs.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dock_outputs)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.dock_project_tree = QtWidgets.QDockWidget(MainWindow)
        self.dock_project_tree.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dock_project_tree.setObjectName("dock_project_tree")
        self.dockWidgetContents_4 = QtWidgets.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(8, 8, 8, 8)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tree_view_projects = QtWidgets.QTreeView(self.dockWidgetContents_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_view_projects.sizePolicy().hasHeightForWidth())
        self.tree_view_projects.setSizePolicy(sizePolicy)
        self.tree_view_projects.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_view_projects.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree_view_projects.setRootIsDecorated(False)
        self.tree_view_projects.setObjectName("tree_view_projects")
        self.tree_view_projects.header().setVisible(False)
        self.horizontalLayout_2.addWidget(self.tree_view_projects)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.button_add = QtWidgets.QToolButton(self.dockWidgetContents_4)
        self.button_add.setAutoRaise(True)
        self.button_add.setObjectName("button_add")
        self.verticalLayout_3.addWidget(self.button_add)
        self.button_up = QtWidgets.QToolButton(self.dockWidgetContents_4)
        self.button_up.setAutoRaise(True)
        self.button_up.setObjectName("button_up")
        self.verticalLayout_3.addWidget(self.button_up)
        self.button_down = QtWidgets.QToolButton(self.dockWidgetContents_4)
        self.button_down.setAutoRaise(True)
        self.button_down.setObjectName("button_down")
        self.verticalLayout_3.addWidget(self.button_down)
        self.button_del = QtWidgets.QToolButton(self.dockWidgetContents_4)
        self.button_del.setAutoRaise(True)
        self.button_del.setObjectName("button_del")
        self.verticalLayout_3.addWidget(self.button_del)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.dock_project_tree.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dock_project_tree)
        self.action_add_document = QtWidgets.QAction(MainWindow)
        self.action_add_document.setObjectName("action_add_document")
        self.action_settings = QtWidgets.QAction(MainWindow)
        self.action_settings.setObjectName("action_settings")
        self.action_wizard = QtWidgets.QAction(MainWindow)
        self.action_wizard.setObjectName("action_wizard")
        self.action_reload = QtWidgets.QAction(MainWindow)
        self.action_reload.setObjectName("action_reload")
        self.action_move_up = QtWidgets.QAction(MainWindow)
        self.action_move_up.setObjectName("action_move_up")
        self.action_move_down = QtWidgets.QAction(MainWindow)
        self.action_move_down.setObjectName("action_move_down")
        self.action_delete_document = QtWidgets.QAction(MainWindow)
        self.action_delete_document.setObjectName("action_delete_document")
        self.actionAbout_Sphinx_Explorer = QtWidgets.QAction(MainWindow)
        self.actionAbout_Sphinx_Explorer.setObjectName("actionAbout_Sphinx_Explorer")
        self.action_about = QtWidgets.QAction(MainWindow)
        self.action_about.setObjectName("action_about")
        self.action_about_qt = QtWidgets.QAction(MainWindow)
        self.action_about_qt.setObjectName("action_about_qt")
        self.menuFile_F.addAction(self.action_settings)
        self.menuCreate_C.addAction(self.action_wizard)
        self.menuHelp.addAction(self.action_about)
        self.menuHelp.addAction(self.action_about_qt)
        self.menubar.addAction(self.menuFile_F.menuAction())
        self.menubar.addAction(self.menuCreate_C.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.action_wizard)
        self.toolBar.addAction(self.action_settings)

        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(0)
        self.output_tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Sphinx Explorer"))
        self.label_project_2.setText(_translate("MainWindow", "Project"))
        self.label_path_2.setText(_translate("MainWindow", "Path"))
        self.label_2.setText(_translate("MainWindow", "Interpreter"))
        self.label.setText(_translate("MainWindow", "Extensions"))
        self.edit_extension_button.setText(_translate("MainWindow", "..."))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), _translate("MainWindow", "Information"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.auto_class), _translate("MainWindow", "Auto Class"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.epub), _translate("MainWindow", "Epub"))
        self.menuFile_F.setTitle(_translate("MainWindow", "Fi&le(F)"))
        self.menuCreate_C.setTitle(_translate("MainWindow", "Create(&C)"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.dock_outputs.setWindowTitle(_translate("MainWindow", "O&utputs"))
        self.output_tab_widget.setTabText(self.output_tab_widget.indexOf(self.Output), _translate("MainWindow", "Output"))
        self.output_tab_widget.setTabText(self.output_tab_widget.indexOf(self.Error), _translate("MainWindow", "Error"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.dock_project_tree.setWindowTitle(_translate("MainWindow", "Pro&ject List"))
        self.button_add.setText(_translate("MainWindow", "..."))
        self.button_up.setText(_translate("MainWindow", "..."))
        self.button_down.setText(_translate("MainWindow", "..."))
        self.button_del.setText(_translate("MainWindow", "..."))
        self.action_add_document.setText(_translate("MainWindow", "Add Document"))
        self.action_add_document.setToolTip(_translate("MainWindow", "Add Document"))
        self.action_settings.setText(_translate("MainWindow", "&Settings..."))
        self.action_settings.setToolTip(_translate("MainWindow", "Settings"))
        self.action_settings.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.action_wizard.setText(_translate("MainWindow", "&wizard mode"))
        self.action_wizard.setToolTip(_translate("MainWindow", "wizard mode"))
        self.action_reload.setText(_translate("MainWindow", "reload"))
        self.action_reload.setToolTip(_translate("MainWindow", "reload"))
        self.action_reload.setShortcut(_translate("MainWindow", "F5"))
        self.action_move_up.setText(_translate("MainWindow", "Move up"))
        self.action_move_up.setToolTip(_translate("MainWindow", "Move up"))
        self.action_move_up.setShortcut(_translate("MainWindow", "Ctrl+Up"))
        self.action_move_down.setText(_translate("MainWindow", "Move down"))
        self.action_move_down.setToolTip(_translate("MainWindow", "Move down"))
        self.action_move_down.setShortcut(_translate("MainWindow", "Ctrl+Down"))
        self.action_delete_document.setText(_translate("MainWindow", "Delete document"))
        self.action_delete_document.setToolTip(_translate("MainWindow", "Delete document"))
        self.action_delete_document.setShortcut(_translate("MainWindow", "Del"))
        self.actionAbout_Sphinx_Explorer.setText(_translate("MainWindow", "About Sphinx Explorer"))
        self.action_about.setText(_translate("MainWindow", "&About Sphinx Explorer..."))
        self.action_about.setToolTip(_translate("MainWindow", "About Sphinx Explorer"))
        self.action_about_qt.setText(_translate("MainWindow", "About &Qt..."))
        self.action_about_qt.setToolTip(_translate("MainWindow", "About Qt..."))

from ..property_widget import PropertyWidget
from ..util.QConsoleWidget import QConsoleWidget
