# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/sphinx-explorer/sphinx_explorer/quickstart_dialog.ui'
#
# Created: Thu Mar 30 09:00:35 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(492, 652)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tool_bookmark = QtGui.QToolButton(Dialog)
        self.tool_bookmark.setObjectName("tool_bookmark")
        self.horizontalLayout.addWidget(self.tool_bookmark)
        self.tool_import = QtGui.QToolButton(Dialog)
        self.tool_import.setObjectName("tool_import")
        self.horizontalLayout.addWidget(self.tool_import)
        self.tool_export = QtGui.QToolButton(Dialog)
        self.tool_export.setObjectName("tool_export")
        self.horizontalLayout.addWidget(self.tool_export)
        self.toolButton = QtGui.QToolButton(Dialog)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout.addWidget(self.toolButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.table_view_property = PropertyWidget(self.splitter)
        self.table_view_property.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.table_view_property.setObjectName("table_view_property")
        self.plain_output = QtGui.QPlainTextEdit(self.splitter)
        self.plain_output.setObjectName("plain_output")
        self.verticalLayout.addWidget(self.splitter)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.action_bookmark = QtGui.QAction(Dialog)
        self.action_bookmark.setObjectName("action_bookmark")
        self.action_import = QtGui.QAction(Dialog)
        self.action_import.setObjectName("action_import")
        self.action_export = QtGui.QAction(Dialog)
        self.action_export.setObjectName("action_export")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Sphinx-Quickstart", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_bookmark.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_import.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tool_export.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.action_bookmark.setText(QtGui.QApplication.translate("Dialog", "Bookmark", None, QtGui.QApplication.UnicodeUTF8))
        self.action_bookmark.setToolTip(QtGui.QApplication.translate("Dialog", "Bookmark", None, QtGui.QApplication.UnicodeUTF8))
        self.action_import.setText(QtGui.QApplication.translate("Dialog", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.action_import.setToolTip(QtGui.QApplication.translate("Dialog", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.action_export.setText(QtGui.QApplication.translate("Dialog", "Export", None, QtGui.QApplication.UnicodeUTF8))
        self.action_export.setToolTip(QtGui.QApplication.translate("Dialog", "Export", None, QtGui.QApplication.UnicodeUTF8))

from sphinx_explorer.property_widget import PropertyWidget
