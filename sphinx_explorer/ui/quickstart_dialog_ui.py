# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/program/sphinx-explorer/sphinx_explorer/ui/quickstart_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(492, 652)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tool_bookmark = QtWidgets.QToolButton(Dialog)
        self.tool_bookmark.setObjectName("tool_bookmark")
        self.horizontalLayout.addWidget(self.tool_bookmark)
        self.tool_import = QtWidgets.QToolButton(Dialog)
        self.tool_import.setObjectName("tool_import")
        self.horizontalLayout.addWidget(self.tool_import)
        self.tool_export = QtWidgets.QToolButton(Dialog)
        self.tool_export.setObjectName("tool_export")
        self.horizontalLayout.addWidget(self.tool_export)
        self.toolButton = QtWidgets.QToolButton(Dialog)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout.addWidget(self.toolButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.table_view_property = PropertyWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.table_view_property.sizePolicy().hasHeightForWidth())
        self.table_view_property.setSizePolicy(sizePolicy)
        self.table_view_property.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.table_view_property.setObjectName("table_view_property")
        self.plain_output = QtWidgets.QPlainTextEdit(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plain_output.sizePolicy().hasHeightForWidth())
        self.plain_output.setSizePolicy(sizePolicy)
        self.plain_output.setObjectName("plain_output")
        self.verticalLayout.addWidget(self.splitter)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.action_bookmark = QtWidgets.QAction(Dialog)
        self.action_bookmark.setObjectName("action_bookmark")
        self.action_import = QtWidgets.QAction(Dialog)
        self.action_import.setObjectName("action_import")
        self.action_export = QtWidgets.QAction(Dialog)
        self.action_export.setObjectName("action_export")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Sphinx-Quickstart"))
        self.tool_bookmark.setText(_translate("Dialog", "..."))
        self.tool_import.setText(_translate("Dialog", "..."))
        self.tool_export.setText(_translate("Dialog", "..."))
        self.toolButton.setText(_translate("Dialog", "..."))
        self.action_bookmark.setText(_translate("Dialog", "Bookmark"))
        self.action_bookmark.setToolTip(_translate("Dialog", "Bookmark"))
        self.action_import.setText(_translate("Dialog", "Import"))
        self.action_import.setToolTip(_translate("Dialog", "Import"))
        self.action_export.setText(_translate("Dialog", "Export"))
        self.action_export.setToolTip(_translate("Dialog", "Export"))

from ..property_widget import PropertyWidget
