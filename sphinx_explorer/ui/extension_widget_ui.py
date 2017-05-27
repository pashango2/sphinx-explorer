# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/toshiyuki/program/sphinx-explorer/sphinx_explorer/ui/extension_widget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(452, 561)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.line_edit_search = QtWidgets.QLineEdit(Form)
        self.line_edit_search.setObjectName("line_edit_search")
        self.verticalLayout.addWidget(self.line_edit_search)
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tree_view_extensions = QtWidgets.QTreeView(self.splitter)
        self.tree_view_extensions.setObjectName("tree_view_extensions")
        self.text_browser_description = QtWidgets.QTextBrowser(self.splitter)
        self.text_browser_description.setObjectName("text_browser_description")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

