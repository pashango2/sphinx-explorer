# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created: Fri Mar 24 11:56:45 2017
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
        self.tool_add_document = QtGui.QToolButton(self.centralwidget)
        self.tool_add_document.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tool_add_document.setObjectName("tool_add_document")
        self.horizontalLayout.addWidget(self.tool_add_document)
        self.tool_setting = QtGui.QToolButton(self.centralwidget)
        self.tool_setting.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.tool_setting.setObjectName("tool_setting")
        self.horizontalLayout.addWidget(self.tool_setting)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtGui.QSplitter(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tree_view_projects = QtGui.QTreeView(self.splitter)
        self.tree_view_projects.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tree_view_projects.setObjectName("tree_view_projects")
        self.table_view_property = PropertyWidget(self.splitter)
        self.table_view_property.setObjectName("table_view_property")
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile_F = QtGui.QMenu(self.menubar)
        self.menuFile_F.setObjectName("menuFile_F")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_quickstart = QtGui.QAction(MainWindow)
        self.action_quickstart.setObjectName("action_quickstart")
        self.action_add_document = QtGui.QAction(MainWindow)
        self.action_add_document.setObjectName("action_add_document")
        self.action_setting = QtGui.QAction(MainWindow)
        self.action_setting.setObjectName("action_setting")
        self.menuFile_F.addAction(self.action_quickstart)
        self.menuFile_F.addAction(self.action_add_document)
        self.menuFile_F.addSeparator()
        self.menuFile_F.addAction(self.action_setting)
        self.menubar.addAction(self.menuFile_F.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Sphinx-explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_button_quick_start.setText(QtGui.QApplication.translate("MainWindow", "sphinx- quickstart", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_add_document.setText(QtGui.QApplication.translate("MainWindow", "add document", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_setting.setText(QtGui.QApplication.translate("MainWindow", "Setting", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile_F.setTitle(QtGui.QApplication.translate("MainWindow", "File(&F)", None, QtGui.QApplication.UnicodeUTF8))
        self.action_quickstart.setText(QtGui.QApplication.translate("MainWindow", "quickstart", None, QtGui.QApplication.UnicodeUTF8))
        self.action_quickstart.setToolTip(QtGui.QApplication.translate("MainWindow", "quickstart", None, QtGui.QApplication.UnicodeUTF8))
        self.action_add_document.setText(QtGui.QApplication.translate("MainWindow", "Add Document", None, QtGui.QApplication.UnicodeUTF8))
        self.action_add_document.setToolTip(QtGui.QApplication.translate("MainWindow", "Add Document", None, QtGui.QApplication.UnicodeUTF8))
        self.action_setting.setText(QtGui.QApplication.translate("MainWindow", "Setting", None, QtGui.QApplication.UnicodeUTF8))
        self.action_setting.setToolTip(QtGui.QApplication.translate("MainWindow", "Setting", None, QtGui.QApplication.UnicodeUTF8))
        self.action_setting.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+S", None, QtGui.QApplication.UnicodeUTF8))

from property_widget import PropertyWidget
