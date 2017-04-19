# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created: Wed Apr 19 12:25:24 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(795, 385)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tree_view_category = QtGui.QTreeView(self.splitter)
        self.tree_view_category.setRootIsDecorated(True)
        self.tree_view_category.setObjectName("tree_view_category")
        self.tree_view_category.header().setVisible(False)
        self.stacked_widget = QtGui.QStackedWidget(self.splitter)
        self.stacked_widget.setFrameShape(QtGui.QFrame.NoFrame)
        self.stacked_widget.setFrameShadow(QtGui.QFrame.Plain)
        self.stacked_widget.setObjectName("stacked_widget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout = QtGui.QVBoxLayout(self.page)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.property_widget = PropertyWidget(self.page)
        self.property_widget.setObjectName("property_widget")
        self.verticalLayout.addWidget(self.property_widget)
        self.stacked_widget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.stacked_widget.addWidget(self.page_2)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

from .property_widget import PropertyWidget
