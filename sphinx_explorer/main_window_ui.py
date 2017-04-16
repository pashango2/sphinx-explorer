# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/sphinx-explorer/sphinx_explorer/main_window.ui'
#
# Created: Mon Apr 17 07:38:55 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tool_button_quick_start = QtGui.QToolButton(self.centralwidget)
        self.tool_button_quick_start.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tool_button_quick_start.setObjectName("tool_button_quick_start")
        self.horizontalLayout.addWidget(self.tool_button_quick_start)
        self.tool_setting = QtGui.QToolButton(self.centralwidget)
        self.tool_setting.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tool_setting.setObjectName("tool_setting")
        self.horizontalLayout.addWidget(self.tool_setting)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tree_view_projects = QtGui.QTreeView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_view_projects.sizePolicy().hasHeightForWidth())
        self.tree_view_projects.setSizePolicy(sizePolicy)
        self.tree_view_projects.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tree_view_projects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree_view_projects.setRootIsDecorated(False)
        self.tree_view_projects.setObjectName("tree_view_projects")
        self.tree_view_projects.header().setVisible(True)
        self.horizontalLayout_2.addWidget(self.tree_view_projects)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.button_add = QtGui.QToolButton(self.centralwidget)
        self.button_add.setAutoRaise(True)
        self.button_add.setObjectName("button_add")
        self.verticalLayout_3.addWidget(self.button_add)
        self.button_up = QtGui.QToolButton(self.centralwidget)
        self.button_up.setAutoRaise(True)
        self.button_up.setObjectName("button_up")
        self.verticalLayout_3.addWidget(self.button_up)
        self.button_down = QtGui.QToolButton(self.centralwidget)
        self.button_down.setAutoRaise(True)
        self.button_down.setObjectName("button_down")
        self.verticalLayout_3.addWidget(self.button_down)
        self.button_del = QtGui.QToolButton(self.centralwidget)
        self.button_del.setAutoRaise(True)
        self.button_del.setObjectName("button_del")
        self.verticalLayout_3.addWidget(self.button_del)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile_F = QtGui.QMenu(self.menubar)
        self.menuFile_F.setObjectName("menuFile_F")
        self.menuCreate_C = QtGui.QMenu(self.menubar)
        self.menuCreate_C.setObjectName("menuCreate_C")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dock_outputs = QtGui.QDockWidget(MainWindow)
        self.dock_outputs.setObjectName("dock_outputs")
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.plain_output = QConsoleWidget(self.dockWidgetContents)
        self.plain_output.setObjectName("plain_output")
        self.verticalLayout_2.addWidget(self.plain_output)
        self.dock_outputs.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dock_outputs)
        self.action_add_document = QtGui.QAction(MainWindow)
        self.action_add_document.setObjectName("action_add_document")
        self.action_settings = QtGui.QAction(MainWindow)
        self.action_settings.setObjectName("action_settings")
        self.action_wizard = QtGui.QAction(MainWindow)
        self.action_wizard.setObjectName("action_wizard")
        self.action_apidoc = QtGui.QAction(MainWindow)
        self.action_apidoc.setObjectName("action_apidoc")
        self.action_reload = QtGui.QAction(MainWindow)
        self.action_reload.setObjectName("action_reload")
        self.action_move_up = QtGui.QAction(MainWindow)
        self.action_move_up.setObjectName("action_move_up")
        self.action_move_down = QtGui.QAction(MainWindow)
        self.action_move_down.setObjectName("action_move_down")
        self.action_delete_document = QtGui.QAction(MainWindow)
        self.action_delete_document.setObjectName("action_delete_document")
        self.menuFile_F.addAction(self.action_settings)
        self.menuCreate_C.addAction(self.action_wizard)
        self.menuCreate_C.addAction(self.action_apidoc)
        self.menubar.addAction(self.menuFile_F.menuAction())
        self.menubar.addAction(self.menuCreate_C.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Sphinx Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_button_quick_start.setText(QtGui.QApplication.translate("MainWindow", "Create", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_setting.setText(QtGui.QApplication.translate("MainWindow", "Setting", None, QtGui.QApplication.UnicodeUTF8))
        self.button_add.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.button_up.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.button_down.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.button_del.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile_F.setTitle(QtGui.QApplication.translate("MainWindow", "File(&F)", None, QtGui.QApplication.UnicodeUTF8))
        self.menuCreate_C.setTitle(QtGui.QApplication.translate("MainWindow", "Create(&C)", None, QtGui.QApplication.UnicodeUTF8))
        self.dock_outputs.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Outputs", None, QtGui.QApplication.UnicodeUTF8))
        self.action_add_document.setText(QtGui.QApplication.translate("MainWindow", "Add Document", None, QtGui.QApplication.UnicodeUTF8))
        self.action_add_document.setToolTip(QtGui.QApplication.translate("MainWindow", "Add Document", None, QtGui.QApplication.UnicodeUTF8))
        self.action_settings.setText(QtGui.QApplication.translate("MainWindow", "Settings...", None, QtGui.QApplication.UnicodeUTF8))
        self.action_settings.setToolTip(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.action_settings.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+S", None, QtGui.QApplication.UnicodeUTF8))
        self.action_wizard.setText(QtGui.QApplication.translate("MainWindow", "wizard mode", None, QtGui.QApplication.UnicodeUTF8))
        self.action_wizard.setToolTip(QtGui.QApplication.translate("MainWindow", "wizard mode", None, QtGui.QApplication.UnicodeUTF8))
        self.action_apidoc.setText(QtGui.QApplication.translate("MainWindow", "apidoc", None, QtGui.QApplication.UnicodeUTF8))
        self.action_apidoc.setToolTip(QtGui.QApplication.translate("MainWindow", "apidoc", None, QtGui.QApplication.UnicodeUTF8))
        self.action_reload.setText(QtGui.QApplication.translate("MainWindow", "リロード", None, QtGui.QApplication.UnicodeUTF8))
        self.action_reload.setToolTip(QtGui.QApplication.translate("MainWindow", "リロード", None, QtGui.QApplication.UnicodeUTF8))
        self.action_reload.setShortcut(QtGui.QApplication.translate("MainWindow", "F5", None, QtGui.QApplication.UnicodeUTF8))
        self.action_move_up.setText(QtGui.QApplication.translate("MainWindow", "Move up", None, QtGui.QApplication.UnicodeUTF8))
        self.action_move_up.setToolTip(QtGui.QApplication.translate("MainWindow", "Move up", None, QtGui.QApplication.UnicodeUTF8))
        self.action_move_up.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Up", None, QtGui.QApplication.UnicodeUTF8))
        self.action_move_down.setText(QtGui.QApplication.translate("MainWindow", "Move down", None, QtGui.QApplication.UnicodeUTF8))
        self.action_move_down.setToolTip(QtGui.QApplication.translate("MainWindow", "Move down", None, QtGui.QApplication.UnicodeUTF8))
        self.action_move_down.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Down", None, QtGui.QApplication.UnicodeUTF8))
        self.action_delete_document.setText(QtGui.QApplication.translate("MainWindow", "Delete document", None, QtGui.QApplication.UnicodeUTF8))
        self.action_delete_document.setToolTip(QtGui.QApplication.translate("MainWindow", "Delete document", None, QtGui.QApplication.UnicodeUTF8))
        self.action_delete_document.setShortcut(QtGui.QApplication.translate("MainWindow", "Del", None, QtGui.QApplication.UnicodeUTF8))

from .util.QConsoleWidget import QConsoleWidget
